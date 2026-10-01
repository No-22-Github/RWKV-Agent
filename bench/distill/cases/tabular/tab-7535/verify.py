# DISTILL-CANARY-bb6a8a85 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/wash_orders_2026-08.csv"]))
total = Decimal("0")
for r in rows:
    if r["月份"] == "2026-08":
        total += Decimal(r["金额"]) - Decimal(r["赔付"])
print(json.dumps({"expected_number": float(total)}))
