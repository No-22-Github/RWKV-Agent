# DISTILL-CANARY-082b263b : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

lines = [line for line in case["files"]["fleece-register.txt"].splitlines() if line.strip()]
skirted = [line for line in lines if "skirted" in line]
print(json.dumps({"expected_number": len(skirted)}))
