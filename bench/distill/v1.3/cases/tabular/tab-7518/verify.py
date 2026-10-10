# DISTILL-CANARY-4f1eecbd : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/market_sales.csv"]))
pos = Decimal("0")
for r in rows:
    if r["sale_month"] == "2026-08":
        pos += Decimal(r["amount"])
rows = csv.DictReader(io.StringIO(case["files"]["data/market_credits.csv"]))
neg = Decimal("0")
for r in rows:
    if r["credit_month"] == "2026-08":
        neg += Decimal(r["amount"])
print(json.dumps({"expected_number": float(pos - neg)}))
