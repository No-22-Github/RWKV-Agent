# DISTILL-CANARY-1e6b4a7d : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["results/run-2026-09-14.log"]
failed = [line for line in text.splitlines() if line.strip().endswith(" error")]
print(json.dumps({"expected_number": len(failed)}))
