# DISTILL-CANARY-392c1915 : distillation case
import json

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/archive.jsonl"].splitlines() if line.strip()]
ids = [json.loads(line)["request_id"] for line in lines]
print(json.dumps({"expected_number": len(set(ids))}))
