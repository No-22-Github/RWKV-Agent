# DISTILL-CANARY-161a01b2 : distillation case
import json

case = json.load(open("case.json"))
chairs = {}
for line in case["files"]["governance/board-chairs.txt"].splitlines():
    fields = [field.strip() for field in line.split("|")]
    if len(fields) == 3:
        chairs[fields[0]] = fields[2]
print(json.dumps({"expected_string": chairs["architecture review board"]}))
