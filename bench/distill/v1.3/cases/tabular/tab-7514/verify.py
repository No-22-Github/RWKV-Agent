# DISTILL-CANARY-01b23231 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/cafe_register.csv"]))
groups = {}
for r in rows:
    if r["sale_month"] == "2026-06":
        groups.setdefault(r["drink_line"], Decimal("0"))
        groups[r["drink_line"]] += Decimal(r["sales"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
