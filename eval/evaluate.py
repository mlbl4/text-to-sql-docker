"""Execution-accuracy evaluation of the Text-to-SQL system.

For each question in questions.json:
  1. ask the inference API for SQL (the model's answer)
  2. run the model's SQL and the correct (gold) SQL through the query service
  3. compare the two result sets

A prediction is correct when it returns the same rows as the gold SQL.
Column names, column order and row order are ignored; numbers are rounded to 2 decimals.

Run inside the Compose network, e.g.:
  docker run --rm --network text-to-sql-docker_backend --user "$(id -u):$(id -g)" \
    -v "$(pwd)/eval:/eval" text2sql-gui:0.1 python /eval/evaluate.py
"""
import json
import os
import time
from pathlib import Path

import requests

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://inference:8000")
QUERY_URL = os.getenv("QUERY_URL", "http://query:8001")
HERE = Path(__file__).parent


def run_sql(sql):
    """Return (rows, error). Exactly one of them is None."""
    r = requests.post(f"{QUERY_URL}/run-sql", json={"sql": sql}, timeout=30)
    if r.status_code != 200:
        return None, r.json().get("detail", r.text)
    return r.json()["rows"], None


def normalize(rows):
    """Make result sets comparable: round numbers, ignore row and column order."""
    def value(v):
        return round(v, 2) if isinstance(v, float) else v
    return sorted((tuple(sorted((value(v) for v in row), key=repr)) for row in rows), key=repr)


def main():
    questions = json.loads((HERE / "questions.json").read_text())
    results = []

    for q in questions:
        start = time.time()
        r = requests.post(f"{INFERENCE_URL}/generate-sql",
                          json={"question": q["question"]}, timeout=180)
        r.raise_for_status()
        predicted_sql = r.json()["sql"]
        seconds = round(time.time() - start, 2)

        gold_rows, gold_error = run_sql(q["gold_sql"])
        if gold_error:
            raise RuntimeError(f"Gold SQL of question {q['id']} failed: {gold_error}")

        pred_rows, pred_error = run_sql(predicted_sql)
        if pred_error:
            outcome = "sql_error"
        elif normalize(pred_rows) == normalize(gold_rows):
            outcome = "correct"
        else:
            outcome = "wrong_result"

        results.append({**q, "predicted_sql": predicted_sql, "outcome": outcome,
                        "error": pred_error, "seconds": seconds})
        print(f"[{q['id']:>2}] {outcome:<12} {seconds:>6}s  {q['question']}")

    total = len(results)
    counts = {k: sum(r["outcome"] == k for r in results)
              for k in ("correct", "wrong_result", "sql_error")}
    avg_seconds = round(sum(r["seconds"] for r in results) / total, 2)

    print("\n=== Summary ===")
    print(f"Execution accuracy: {counts['correct']}/{total} ({100 * counts['correct'] / total:.0f}%)")
    print(f"Wrong result:       {counts['wrong_result']}/{total}")
    print(f"SQL error:          {counts['sql_error']}/{total}")
    print(f"Average time:       {avg_seconds}s per question")

    out = HERE / "results.json"
    summary = {"accuracy": counts["correct"] / total, **counts, "avg_seconds": avg_seconds}
    out.write_text(json.dumps({"summary": summary, "results": results},
                              indent=2, ensure_ascii=False))
    print(f"\nDetailed results saved to {out}")


if __name__ == "__main__":
    main()
