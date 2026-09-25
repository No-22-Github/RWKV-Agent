# DISTILL-CANARY-77dd123c : distillation case
import json

case = json.load(open("case.json"))
periods = {}
for line in case["files"]["runbook/records-retention.txt"].splitlines():
    record, period = [part.strip() for part in line.split("=")]
    periods[record] = period
print(json.dumps({"expected_string": periods["dive log records"]}))
