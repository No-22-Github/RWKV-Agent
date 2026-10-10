# DISTILL-CANARY-95ac24e4 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/sessions_2026-09.csv"]))
total = Decimal("0")
for r in rows:
    if r["session_month"] == "2026-09" and r["plan"] == "Commute":
        total += Decimal(r["kwh_delivered"])
print(json.dumps({"expected_number": float(total)}))
