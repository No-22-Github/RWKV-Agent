# DISTILL-CANARY-9ca8f1d4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["statement_2026-08.csv"])))
balance = 0.0
for r in rows:
    amt = float(r["amount"])
    if r["direction"] == "CR":
        balance += amt
    else:
        balance -= amt
print(json.dumps({"expected_number": round(balance, 2)}))
