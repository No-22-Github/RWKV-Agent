# DISTILL-CANARY-46019432 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["governance/service-register.txt"].splitlines():
    fields = [field.strip() for field in line.split("|")]
    if len(fields) == 3:
        rows[fields[0]] = fields[2]
print(json.dumps({"expected_string": rows["berth-planner"]}))
