# DISTILL-CANARY-71ba83d6 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["shipping/freight_register.csv"]))
total = Decimal("0")
for r in rows:
    if r["destination_state"] == "Ohio" and r["ship_month"] == "2026-09":
        total += Decimal(r["freight_cost"])
print(json.dumps({"expected_number": float(total)}))
