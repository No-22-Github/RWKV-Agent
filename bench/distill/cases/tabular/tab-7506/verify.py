# DISTILL-CANARY-c2acbd1a : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/class_sessions.csv"]))
total = Decimal("0")
count = 0
for r in rows:
    if r["session_month"] == "2026-06" and r["class_name"] == "Yoga Flow":
        total += Decimal(r["attendees"])
        count += 1
print(json.dumps({"expected_number": float(total / count)}))
