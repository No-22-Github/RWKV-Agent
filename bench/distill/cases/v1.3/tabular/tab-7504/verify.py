# DISTILL-CANARY-9acd77ea : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/overtime_log.csv"]))
total = Decimal("0")
for r in rows:
    if r["entry_month"] == "2026-08" and r["task"] == "Hardscape":
        total += Decimal(r["ot_approved"])
print(json.dumps({"expected_number": float(total)}))
