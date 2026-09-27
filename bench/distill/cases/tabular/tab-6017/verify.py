# DISTILL-CANARY-3ef4463f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["accounts/invoices_2026-08.csv"])))
count = sum(1 for r in rows if float(r["amount"]) > 2000.0)
print(json.dumps({"expected_number": count}))
