# DISTILL-CANARY-41db4241 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/sales_ledger.csv"]))
pos = Decimal("0")
for r in rows:
    if r["结算月份"] == "2026-08":
        pos += Decimal(r["金额"])
rows = csv.DictReader(io.StringIO(case["files"]["data/credits_ledger.csv"]))
neg = Decimal("0")
for r in rows:
    if r["结算月份"] == "2026-08":
        neg += Decimal(r["金额"])
print(json.dumps({"expected_number": float(pos - neg)}))
