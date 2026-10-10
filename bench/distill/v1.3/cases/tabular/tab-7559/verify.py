# DISTILL-CANARY-932badb7 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/register_2026-08.csv"]))
total = Decimal("0")
for r in rows:
    if r["entry_month"] == "2026-08":
        total += Decimal(r["fee_gbp"]) - Decimal(r["deduction_gbp"])
print(json.dumps({"expected_number": float(total)}))
