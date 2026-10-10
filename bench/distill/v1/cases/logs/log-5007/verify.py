# DISTILL-CANARY-4d5589d4 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in case["files"]["logs/router.jsonl"].splitlines() if line.strip()]
total = sum(row["bytes_out"] for row in rows)
print(json.dumps({"expected_number": total}))
