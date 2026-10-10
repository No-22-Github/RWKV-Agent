# DISTILL-CANARY-2768bebd : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/stall_sales.csv"]))
groups = {}
for r in rows:
    if r["order_month"] == "2026-05" and r["house_account"] == "N":
        groups.setdefault(r["product_line"], Decimal("0"))
        groups[r["product_line"]] += Decimal(r["sales"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
