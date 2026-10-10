# DISTILL-CANARY-21448a7e : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['routes/stop-days.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['Bramblecote']}))
