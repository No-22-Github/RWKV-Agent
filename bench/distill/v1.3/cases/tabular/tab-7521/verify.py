# DISTILL-CANARY-90aa1f51 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/rental_charges.csv"]))
pos = Decimal("0")
for r in rows:
    if r["charge_month"] == "2026-03":
        pos += Decimal(r["amount"])
rows = csv.DictReader(io.StringIO(case["files"]["data/return_credits.csv"]))
neg = Decimal("0")
for r in rows:
    if r["credit_month"] == "2026-03":
        neg += Decimal(r["amount"])
print(json.dumps({"expected_number": float(pos - neg)}))
