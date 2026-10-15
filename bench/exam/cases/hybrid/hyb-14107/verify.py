# EXAM-CANARY-f86977bd : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import datetime as dt
for line in case["files"]["project/plan.md"].splitlines():
    if "Beta" in line:
        d = dt.date.fromisoformat(line.split("：")[1].strip())
print(json.dumps({"expected_number": (d - dt.date(2026, 9, 16)).days}))
