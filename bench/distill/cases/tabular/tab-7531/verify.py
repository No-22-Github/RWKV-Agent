# DISTILL-CANARY-074eef86 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/enrolments_2026-08.csv"]))
total = Decimal("0")
for r in rows:
    if r["enrol_month"] == "2026-08" and r["program"] == "Learn-to-Swim":
        total += Decimal(r["fee_gbp"])
print(json.dumps({"expected_number": float(total)}))
