# DISTILL-CANARY-5454d805 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['market/circular-days.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['weekly price circular']}))
