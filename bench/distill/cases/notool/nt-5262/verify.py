# DISTILL-CANARY-f24693ad : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['drawings/series-index.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['pipework layouts']}))
