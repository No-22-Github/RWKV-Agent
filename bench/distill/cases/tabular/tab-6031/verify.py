# DISTILL-CANARY-ef0a504a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
inv = list(csv.DictReader(io.StringIO(case["files"]["books/invoices_2026-08.csv"])))
pay = list(csv.DictReader(io.StringIO(case["files"]["books/payments_2026-08.csv"])))


def clean(s):
    return float(s.replace("$", "").replace(",", ""))


out = sum(clean(r["amount"]) for r in inv) - sum(clean(r["amount"]) for r in pay)
print(json.dumps({"expected_number": round(out, 2)}))
