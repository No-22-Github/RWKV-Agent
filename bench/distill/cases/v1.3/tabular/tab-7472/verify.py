# DISTILL-CANARY-844ae394 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/ledger_2026-08.csv"])))
ledger = sum(Decimal(r["应收金额"]) for r in rows)
rows = list(csv.DictReader(io.StringIO(case["files"]["data/receipts_2026-08.csv"])))
receipts = sum(Decimal(r["实收金额"]) for r in rows)
print(json.dumps({"expected_number": float(ledger - receipts)}))
