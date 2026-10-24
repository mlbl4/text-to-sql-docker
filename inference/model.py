import os
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-Coder-0.5B-Instruct")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "/app/schema.sql")

SYSTEM_PROMPT = (
    "You are an expert PostgreSQL assistant. Given a database schema and a "
    "question, answer with a single SQL query and nothing else."
)


def load_model():
    """Load tokenizer and model once. Slow: call it at startup, not per request."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
    model.eval()
    return tokenizer, model


def generate_sql(tokenizer, model, schema, question, max_new_tokens=256):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Schema:\n{schema}\n\nQuestion: {question}"},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)

    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many orders were placed by customers from Alicante?"
    schema = Path(SCHEMA_PATH).read_text()

    start = time.time()
    tokenizer, model = load_model()
    print(f"Model ready in {time.time() - start:.1f}s")

    start = time.time()
    sql = generate_sql(tokenizer, model, schema, question)
    print(f"\nQ: {question}\n{sql}\n({time.time() - start:.1f}s)")