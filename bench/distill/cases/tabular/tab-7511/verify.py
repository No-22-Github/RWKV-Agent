# DISTILL-CANARY-953969c3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/charter_log.csv"]))
n = 0
for r in rows:
    if r["booking_month"] == "2026-07" and r["charter_type"] == "Deep Sea":
        n += 1
print(json.dumps({"expected_number": n}))
