# DISTILL-CANARY-e42f32ee : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/firings.csv"]))
pos = Decimal("0")
for r in rows:
    if r["fire_month"] == "2026-09":
        pos += Decimal(r["pieces_fired"])
rows = csv.DictReader(io.StringIO(case["files"]["data/market_sales.csv"]))
neg = Decimal("0")
for r in rows:
    if r["sale_month"] == "2026-09":
        neg += Decimal(r["pieces_sold"])
print(json.dumps({"expected_number": float(pos - neg)}))
