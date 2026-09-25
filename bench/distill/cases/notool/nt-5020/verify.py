# DISTILL-CANARY-46e5072c : distillation case
import json

case = json.load(open("case.json"))
total = 0.0
for line in case["files"]["houses/hdd_log.csv"].splitlines():
    fields = line.split(",")
    total += float(fields[2]) - float(fields[1])
print(json.dumps({"expected_number": total}))
