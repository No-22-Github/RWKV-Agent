# DISTILL-CANARY-363aa460 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/service_charges.csv"]))
total = Decimal("0")
for r in rows:
    if r["visit_month"] == "2026-09" and r["species"] == "Dog":
        total += Decimal(r["final_amount"])
print(json.dumps({"expected_number": float(total)}))
