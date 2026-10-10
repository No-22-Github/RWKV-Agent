# DISTILL-CANARY-9f0445d7 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

register = case["files"]["boathouse-register.txt"]
rows = [line for line in register.splitlines() if "training row" in line]
print(json.dumps({"expected_number": len(rows)}))
