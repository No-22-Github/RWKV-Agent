# DISTILL-CANARY-fd72315f : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
ch = csv.DictReader(io.StringIO(case["files"]["data/charges_2026-09.csv"]))
pay = csv.DictReader(io.StringIO(case["files"]["data/payments_2026-09.csv"]))
a = sum((Decimal(r["settled_total"]) for r in ch), Decimal("0"))
b = sum((Decimal(r["amount_gbp"]) for r in pay), Decimal("0"))
print(json.dumps({"expected_number": float(a - b)}))
