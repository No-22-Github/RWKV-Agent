# DISTILL-CANARY-1be63781 : distillation case
import json

case = json.load(open("case.json"))
owners = {}
for line in case["files"]["engineering/repository-ownership.txt"].splitlines():
    fields = [field.strip() for field in line.split("|")]
    if len(fields) == 3:
        owners[fields[0]] = fields[2]
print(json.dumps({"expected_string": owners["audit-trail-exporter"]}))
