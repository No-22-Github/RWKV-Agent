# DISTILL-CANARY-910b8d68 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['duties/duty-owners.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['livestock welfare round']}))
