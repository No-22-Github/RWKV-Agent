# DISTILL-CANARY-90ee677b : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['collections/series-index.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['field notebooks']}))
