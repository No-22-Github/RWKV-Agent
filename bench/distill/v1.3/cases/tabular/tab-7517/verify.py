# DISTILL-CANARY-2784f0d5 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/plant_sales.tsv"]), delimiter="	")
groups = {}
for r in rows:
    if r["order_month"] == "2026-05":
        groups.setdefault(r["plant_family"], Decimal("0"))
        groups[r["plant_family"]] += Decimal(r["sales"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
