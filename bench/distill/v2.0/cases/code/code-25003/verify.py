# DISTILL-CANARY-5b2c81f0 : distillation case
import json

case = json.load(open("case.json"))
report = json.loads(case["files"]["results/run_verdict.json"])
failed = [entry["name"] for entry in report["cases"] if entry["outcome"] == "failed"]
print(json.dumps({"expected_number": len(failed)}))
