# DISTILL-CANARY-1e053f71 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['governance/notification-bodies.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['serious injury to a resident']}))
