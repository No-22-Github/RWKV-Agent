# DISTILL-CANARY-45c1b3be : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/drink_sales.csv"]))
total = Decimal("0")
for r in rows:
    if r["销售月份"] == "2026-08" and r["饮品系列"] == "桂花乌龙":
        total += Decimal(r["销售额"])
print(json.dumps({"expected_number": float(total)}))
