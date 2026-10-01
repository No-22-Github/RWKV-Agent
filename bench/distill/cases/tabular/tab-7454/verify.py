# DISTILL-CANARY-5314b2a0 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/seafood_sales_2026-08.csv"])))
total = sum(Decimal(r["金额"]) for r in rows if r["组别"] == "鲜货组")
print(json.dumps({"expected_number": float(total)}))
