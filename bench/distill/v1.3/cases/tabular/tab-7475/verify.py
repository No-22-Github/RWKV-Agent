# DISTILL-CANARY-1152627b : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/sales_ledger_2026-09.csv"])))
ledger = sum(Decimal(r["金额"]) for r in rows)
rows = list(csv.DictReader(io.StringIO(case["files"]["data/bank_receipts_2026-09.csv"])))
sep = sum(Decimal(r["金额"]) for r in rows if r["记账日"].startswith("2026-09"))
print(json.dumps({"expected_number": float(ledger - sep)}))
