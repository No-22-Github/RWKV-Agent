# DISTILL-CANARY-b32323ed : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
inv = list(csv.DictReader(io.StringIO(case["files"]["billing/invoices_2026-08.csv"])))
rec = list(csv.DictReader(io.StringIO(case["files"]["billing/receipts_2026-08.csv"])))
out = sum(float(r["amount"]) for r in inv) - sum(float(r["amount"]) for r in rec)
print(json.dumps({"expected_number": round(out, 2)}))
