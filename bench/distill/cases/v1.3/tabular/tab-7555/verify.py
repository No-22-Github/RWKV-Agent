# DISTILL-CANARY-e5256f89 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
inv = csv.DictReader(io.StringIO(case["files"]["data/invoices_2026-09.csv"]))
rec = csv.DictReader(io.StringIO(case["files"]["data/receipts_2026-09.csv"]))
a = sum((Decimal(r["fee_gbp"]) for r in inv), Decimal("0"))
b = sum((Decimal(r["amount_gbp"]) for r in rec if r["value_month"] == "2026-09"), Decimal("0"))
print(json.dumps({"expected_number": float(a - b)}))
