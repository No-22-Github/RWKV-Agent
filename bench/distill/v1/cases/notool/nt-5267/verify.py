# DISTILL-CANARY-3c1bad33 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['duties/post-responsibilities.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['playground equipment check']}))
