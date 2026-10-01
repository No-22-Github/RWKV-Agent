# DISTILL-CANARY-5d3fa7d5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/bookings_2026-09.csv"]))
n = 0
for r in rows:
    if r["booking_month"] == "2026-09" and r["tour"] == "Sunset Tour":
        n += 1
print(json.dumps({"expected_number": n}))
