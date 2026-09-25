# DISTILL-CANARY-3d5a8fc2 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["governance/signoff-list.txt"].splitlines():
    check, role = [part.strip() for part in line.split("=")]
    rows[check] = role
print(json.dumps({"expected_string": rows["recall notices"]}))
