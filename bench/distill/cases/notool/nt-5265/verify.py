# DISTILL-CANARY-a9d2e7a0 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['records/measurement-units.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['feed weight']}))
