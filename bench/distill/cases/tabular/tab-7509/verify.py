# DISTILL-CANARY-b4b1fefc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/swim_checkins.csv"]))
n = 0
for r in rows:
    if r["checkin_month"] == "2026-06" and r["program"] == "Aqua Fit" and r["lane"] == "Slow":
        n += 1
print(json.dumps({"expected_number": n}))
