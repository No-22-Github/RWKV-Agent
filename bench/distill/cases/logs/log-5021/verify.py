# DISTILL-CANARY-35af7d80 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in case["files"]["logs/weighbridge.jsonl"].splitlines() if line.strip()]
north = [row["load_kg"] for row in rows if row["lane"] == "north"]
print(json.dumps({"expected_number": max(north)}))
