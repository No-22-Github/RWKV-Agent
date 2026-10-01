# DISTILL-CANARY-4ecfacd1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/sessions_2026-09.csv"]))
n = 0
for r in rows:
    if r["session_month"] == "2026-09" and r["session"] == "Wheel Taster":
        n += 1
print(json.dumps({"expected_number": n}))
