# DISTILL-CANARY-bdb79cd1 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['records/reading-units.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['silage clamp weight']}))
