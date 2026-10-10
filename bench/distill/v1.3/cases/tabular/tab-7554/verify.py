# DISTILL-CANARY-30b60b04 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/workroom_2026-08.csv"]))
total = Decimal("0")
for r in rows:
    total += Decimal(r["fee_gbp"]) - Decimal(r["allowance_gbp"])
print(json.dumps({"expected_number": float(total)}))
