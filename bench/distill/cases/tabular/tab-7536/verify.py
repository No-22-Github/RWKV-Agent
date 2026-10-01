# DISTILL-CANARY-dbd6015a : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/boat_hire_2026-08.csv"]))
total = Decimal("0")
for r in rows:
    if r["hire_date"] in ("2026-08-22", "08/22/2026"):
        total += Decimal(r["fee_gbp"])
print(json.dumps({"expected_number": float(total)}))
