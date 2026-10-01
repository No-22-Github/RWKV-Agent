# DISTILL-CANARY-f86148f8 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/cafe_sales_2026-09.csv"])))
total = sum(Decimal(r["金额"]) for r in rows if r["渠道"] == "外带")
print(json.dumps({"expected_number": float(total)}))
