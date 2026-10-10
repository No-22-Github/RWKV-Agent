# DISTILL-CANARY-8970c41b : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/pen_sales.csv"]))
groups = {}
for r in rows:
    if r["销售月份"] == "2026-09":
        groups.setdefault(r["笔类"], Decimal("0"))
        groups[r["笔类"]] += Decimal(r["销售额"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
