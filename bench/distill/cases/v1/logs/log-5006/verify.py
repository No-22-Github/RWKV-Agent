# DISTILL-CANARY-82ac55e7 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in case["files"]["logs/gateway.jsonl"].splitlines() if line.strip()]
total = sum(row["bytes"] for row in rows if row["route"] == "/v2/ledger")
print(json.dumps({"expected_number": total}))
