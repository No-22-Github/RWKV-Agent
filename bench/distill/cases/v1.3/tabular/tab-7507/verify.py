# DISTILL-CANARY-5c7edaa8 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/claim_lines.csv"]))
total = Decimal("0")
for r in rows:
    if r["claim_month"] == "2026-09" and r["payer"] == "Bluepeak Dental" and r["billable"] == "Y":
        total += Decimal(r["line_amount"])
print(json.dumps({"expected_number": float(total)}))
