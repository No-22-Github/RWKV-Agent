# DISTILL-CANARY-5a81b8cb : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/wholesale_invoices.csv"]))
total = Decimal("0")
for r in rows:
    if r["invoice_month"] == "2026-08" and r["cafe_chain"] == "Hearth & Honey" and r["status"] == "Settled":
        total += Decimal(r["amount"])
print(json.dumps({"expected_number": float(total)}))
