"""GUI service: a Gradio page that only orchestrates the other two services.

It contains no model and no database logic:
  1. sends the question to the inference API  -> gets SQL
  2. sends that SQL to the query service      -> gets rows
  3. shows the SQL and the result table
"""
import os

import gradio as gr
import pandas as pd
import requests

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://localhost:8000")
QUERY_URL = os.getenv("QUERY_URL", "http://localhost:8001")

EXAMPLES = [
    "How many orders were placed by customers from Alicante?",
    "Which 5 customers spent the most money in total?",
    "What is the best-selling product in each category?",
    "How many orders are in each status?",
]


def error_detail(response):
    """Extract the 'detail' message that FastAPI puts in error responses."""
    try:
        return response.json().get("detail", response.text)
    except ValueError:
        return response.text


def ask(question):
    empty = pd.DataFrame()
    if not question or not question.strip():
        return "", empty, "⚠️ Write a question first."

    # 1) Natural language -> SQL (this call waits until the model finishes)
    try:
        r = requests.post(f"{INFERENCE_URL}/generate-sql",
                          json={"question": question}, timeout=120)
    except requests.RequestException as e:
        return "", empty, f"❌ Inference service unreachable: {e}"
    if r.status_code != 200:
        return "", empty, f"❌ Inference error: {error_detail(r)}"
    answer = r.json()
    sql, gen_seconds = answer["sql"], answer["seconds"]

    # 2) SQL -> rows (the SQL text travels in the body of this new request)
    try:
        r = requests.post(f"{QUERY_URL}/run-sql", json={"sql": sql}, timeout=30)
    except requests.RequestException as e:
        return sql, empty, f"❌ Query service unreachable: {e}"
    if r.status_code != 200:
        # The model wrote SQL that PostgreSQL rejected: show the database's message
        return sql, empty, f"❌ The database rejected the SQL ({gen_seconds}s to generate):\n\n`{error_detail(r)}`"

    result = r.json()
    table = pd.DataFrame(result["rows"], columns=result["columns"])
    status = f"✅ {result['row_count']} row(s) · SQL generated in {gen_seconds}s"
    if result["truncated"]:
        status += " · showing only the first rows"
    return sql, table, status


with gr.Blocks(title="Text-to-SQL") as demo:
    gr.Markdown(
        "# Text-to-SQL\n"
        "Ask a question about the online store in plain English. "
        "A small language model (Qwen2.5-Coder-0.5B) writes the SQL, and a "
        "read-only service runs it on PostgreSQL."
    )
    question = gr.Textbox(label="Question", placeholder="e.g. Which products are the most expensive?")
    button = gr.Button("Ask", variant="primary")
    gr.Examples(EXAMPLES, inputs=question)
    status = gr.Markdown()
    sql_box = gr.Code(label="Generated SQL", language="sql")
    table = gr.Dataframe(label="Result")

    button.click(ask, inputs=question, outputs=[sql_box, table, status])
    question.submit(ask, inputs=question, outputs=[sql_box, table, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
