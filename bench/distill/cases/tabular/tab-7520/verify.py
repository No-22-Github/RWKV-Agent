# DISTILL-CANARY-3f854923 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/fuel_card_charges.csv"]))
pos = Decimal("0")
for r in rows:
    if r["charge_month"] == "2026-08":
        pos += Decimal(r["amount_settled"])
rows = csv.DictReader(io.StringIO(case["files"]["data/fuel_credits.csv"]))
neg = Decimal("0")
for r in rows:
    if r["credit_month"] == "2026-08":
        neg += Decimal(r["credit_amount"])
print(json.dumps({"expected_number": float(pos - neg)}))
