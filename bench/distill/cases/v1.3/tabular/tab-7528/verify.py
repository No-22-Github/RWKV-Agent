# DISTILL-CANARY-96ca178c : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/bean_purchases.csv"]))
groups = {}
for r in rows:
    if r["采购月份"] == "2026-08":
        groups.setdefault(r["产地"], Decimal("0"))
        groups[r["产地"]] += Decimal(r["成交额"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
