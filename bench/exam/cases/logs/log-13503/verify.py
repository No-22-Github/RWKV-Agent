# EXAM-CANARY-5d27e0b9 : exam gap-fill case
import json
case=json.load(open("case.json",encoding="utf-8"))
n=sum(1 for l in case["files"]["logs/app-error.log"].splitlines() if l.startswith("2026-09-12") and " ERROR " in l and "timeout" in l)
print(json.dumps({"expected_number":n}))
