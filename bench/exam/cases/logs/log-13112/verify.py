# EXAM-CANARY-85461788 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
n = 0
for line in case["files"]["ops.log"].splitlines():
    day, _clock, svc, verb, *_ = line.split()
    if day == "2026-09-15" and svc == "nginx" and verb == "restarted":
        n += 1
print(json.dumps({"expected_number": n}))
