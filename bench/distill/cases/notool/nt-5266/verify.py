# DISTILL-CANARY-9d082c68 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['duties/post-duties.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['monthly boiler check']}))
