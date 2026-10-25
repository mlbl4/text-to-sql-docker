import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from model import MODEL_ID, SCHEMA_PATH, generate_sql, load_model

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs ONCE when the server starts: load the model and the schema
    print("Loading model...")
    state["tokenizer"], state["model"] = load_model()
    state["schema"] = Path(SCHEMA_PATH).read_text()
    print("Model ready")
    yield
    # Runs once when the server stops
    state.clear()


app = FastAPI(title="Text-to-SQL inference API", lifespan=lifespan)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class SQLResponse(BaseModel):
    question: str
    sql: str
    seconds: float


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID}


@app.post("/generate-sql", response_model=SQLResponse)
def generate(request: QuestionRequest):
    start = time.time()
    sql = generate_sql(state["tokenizer"], state["model"], state["schema"], request.question)
    return SQLResponse(question=request.question, sql=sql, seconds=round(time.time() - start, 2))