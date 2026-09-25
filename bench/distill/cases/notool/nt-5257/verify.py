# DISTILL-CANARY-c4a001fe : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['notifications/incident-bodies.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['stream pollution']}))
