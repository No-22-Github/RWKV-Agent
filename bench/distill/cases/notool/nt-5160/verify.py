# DISTILL-CANARY-e8017b46 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["quality/signoff-list.txt"].splitlines():
    check, role = [part.strip() for part in line.split("=")]
    rows[check] = role
print(json.dumps({"expected_string": rows["first article inspection"]}))
