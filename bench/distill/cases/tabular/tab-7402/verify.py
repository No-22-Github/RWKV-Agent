# DISTILL-CANARY-4be70a31 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["invoices/billing_export.csv"]))
total = Decimal("0")
for r in rows:
    if r["plan"] == "Team" and r["region"] == "EMEA" and r["billing_month"] == "2026-08":
        total += Decimal(r["amount_usd"])
print(json.dumps({"expected_number": float(total)}))
