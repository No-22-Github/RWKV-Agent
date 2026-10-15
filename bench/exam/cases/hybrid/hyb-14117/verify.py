# EXAM-CANARY-8f5aa2d9 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
n = sum(1 for l in case["files"]["logs/app.log"].splitlines() if l.startswith("2026-09-15") and " ERROR " in l)
yml = case["files"]["conf/alert.yaml"].replace("error_threshold: 12", "error_threshold: %d" % (n + 5))
print(json.dumps({"expected_number": n + 5, "files": {"conf/alert.yaml": yml}}))
