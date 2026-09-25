# DISTILL-CANARY-658dec8c : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

register = case["files"]["season-register.txt"]
extractions = [line for line in register.splitlines() if " - extraction - " in line]
print(json.dumps({"expected_number": len(extractions)}))
