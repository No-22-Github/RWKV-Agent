# DISTILL-CANARY-a7477889 : distillation case
import json

case = json.load(open("case.json"))
turnarounds = {}
for line in case["files"]["runbook/conflict-check.txt"].splitlines():
    check, turnaround = [part.strip() for part in line.split("=")]
    turnarounds[check] = turnaround
print(json.dumps({"expected_string": turnarounds["new client conflict check"]}))
