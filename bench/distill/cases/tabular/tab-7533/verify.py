# DISTILL-CANARY-fdee4d72 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/outbound_2026-09.csv"]))
total = Decimal("0")
for r in rows:
    if r["出库月份"] == "2026-09":
        total += Decimal(r["过磅吨数"])
print(json.dumps({"expected_number": float(total)}))
