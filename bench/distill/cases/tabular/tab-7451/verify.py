# DISTILL-CANARY-6815806c : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/tea_sales_2026-08.csv"])))
total = sum(Decimal(r["金额"]) for r in rows)
print(json.dumps({"expected_number": float(total)}))
