# DISTILL-CANARY-c46b1d93 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["governance/site-designations.txt"].splitlines():
    site, designation = [part.strip() for part in line.split("|")]
    rows[site] = designation
print(json.dumps({"expected_string": rows["the lower meadow"]}))
