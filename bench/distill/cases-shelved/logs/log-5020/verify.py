# DISTILL-CANARY-b09e4c17 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in case["files"]["logs/queue.jsonl"].splitlines() if line.strip()]
total = sum(row["runtime_ms"] for row in rows
            if row["queue"] == "render" and row["outcome"] == "completed")
print(json.dumps({"expected_number": total}))
