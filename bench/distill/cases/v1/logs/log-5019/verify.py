# DISTILL-CANARY-72d8ab35 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in case["files"]["logs/edge.jsonl"].splitlines() if line.strip()]
total = sum(row["bytes"] for row in rows
            if row["path"] == "/img/hero-a.jpg" and row["ts"].startswith("2026-08-14"))
print(json.dumps({"expected_number": total}))
