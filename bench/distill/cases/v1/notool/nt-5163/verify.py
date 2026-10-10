# DISTILL-CANARY-2a83e50f : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["records/site-designations.txt"].splitlines():
    building, designation = [part.strip() for part in line.split("|")]
    rows[building] = designation
print(json.dumps({"expected_string": rows["the old shed"]}))
