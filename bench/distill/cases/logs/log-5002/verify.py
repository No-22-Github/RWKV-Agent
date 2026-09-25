# DISTILL-CANARY-1dd17a12 : distillation case
import json

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/coldstore.log"].splitlines() if line.strip()]
opens = [line for line in lines if line.endswith("event=open door=bay")]
print(json.dumps({"expected_number": len(opens)}))
