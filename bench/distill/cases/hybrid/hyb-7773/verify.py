# DISTILL-CANARY-5e735b17 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["reservations/reservations-2026-09.csv"]))
total = 0.0
for r in rows:
    total += float(r["hours"])
print(json.dumps({"expected_number": round(total, 2)}))
