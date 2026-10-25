"""Query service: runs SQL on PostgreSQL safely and returns the rows as JSON.

Protections (defense in depth):
  1. Connects as a read-only database user (only SELECT permission).
  2. Every transaction is read-only (default_transaction_read_only).
  3. statement_timeout stops queries that run too long.
  4. At most MAX_ROWS rows are returned.
"""
import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "store"),
    "user": os.getenv("DB_USER", "readonly_user"),
    "password": os.getenv("DB_PASSWORD", "readonly"),
}
MAX_ROWS = int(os.getenv("MAX_ROWS", "100"))
STATEMENT_TIMEOUT_MS = int(os.getenv("STATEMENT_TIMEOUT_MS", "5000"))

app = FastAPI(title="Read-only SQL query service")


class SQLRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=5000)


def connect():
    """Open a connection where every query is read-only and time-limited."""
    return psycopg.connect(
        **DB_CONFIG,
        connect_timeout=5,
        options=(
            f"-c statement_timeout={STATEMENT_TIMEOUT_MS} "
            "-c default_transaction_read_only=on"
        ),
    )


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")
    return {"status": "ok"}


@app.post("/run-sql")
def run_sql(request: SQLRequest):
    try:
        with connect() as conn:
            cursor = conn.execute(request.sql)
            if cursor.description is None:
                raise HTTPException(status_code=400, detail="Only queries that return rows are allowed.")
            columns = [col.name for col in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS + 1)  # one extra to detect truncation
    except psycopg.Error as e:
        # Return the database's own error message, so the GUI can show it
        raise HTTPException(status_code=400, detail=str(e).strip())

    truncated = len(rows) > MAX_ROWS
    rows = rows[:MAX_ROWS]
    return {"columns": columns, "rows": rows, "row_count": len(rows), "truncated": truncated}