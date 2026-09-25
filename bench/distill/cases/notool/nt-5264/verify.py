# DISTILL-CANARY-cbf14dcd : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['process/reading-units.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['stock flow']}))
