# DISTILL-CANARY-4f12d9e1 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/honey_intake_2026-09.csv"]))
total = Decimal("0")
for r in rows:
    if r["intake_month"] == "2026-09":
        total += Decimal(r["settled_kg"])
print(json.dumps({"expected_number": float(total)}))
