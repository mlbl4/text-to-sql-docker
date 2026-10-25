import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
SCHEMA = Path("db/init/01_schema.sql").read_text()

print("Loading model...")
start = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
model.eval()
print(f"Model loaded in {time.time() - start:.1f}s")


def generate_sql(question):
    messages = [
        {"role": "system", "content": (
            "You are an expert PostgreSQL assistant. Given a database schema and a "
            "question, answer with a single SQL query and nothing else."
        )},
        {"role": "user", "content": f"Schema:\n{SCHEMA}\n\nQuestion: {question}"},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    print(f"Prompt length: {inputs['input_ids'].shape[1]} tokens")

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=256, do_sample=False)

    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


questions = [
    "How many orders were placed by customers from Alicante?",
    "Which 5 customers spent the most money in total?",
    "What is the best-selling product in each category?",
]

for q in questions:
    start = time.time()
    sql = generate_sql(q)
    print(f"\nQ: {q}\n{sql}\n({time.time() - start:.1f}s)")