# DISTILL-CANARY-dee88370 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/vinyl_sales_2026-09.csv"]))
total = Decimal("0")
for r in rows:
    if r["genre"] == "Jazz" and r["sale_month"] == "2026-09":
        total += Decimal(r["amount_gbp"])
print(json.dumps({"expected_number": float(total)}))
