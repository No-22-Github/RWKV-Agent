# DISTILL-CANARY-8e2a55c7 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["office/issue-routing.txt"].splitlines():
    issue, team = [part.strip() for part in line.split("=")]
    rows[issue] = team
print(json.dumps({"expected_string": rows["damaged parcel claims"]}))
