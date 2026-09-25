# DISTILL-CANARY-f1d516bb : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['services/collection-days.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['clinical waste']}))
