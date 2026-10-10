# DISTILL-CANARY-7f1c86b4 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["estates/site-designations.txt"].splitlines():
    building, designation = [part.strip() for part in line.split("|")]
    rows[building] = designation
print(json.dumps({"expected_string": rows["the annexe"]}))
