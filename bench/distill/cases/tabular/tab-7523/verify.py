# DISTILL-CANARY-9dde67c0 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/site_fees.csv"]))
total = Decimal("0")
for r in rows:
    if r["入住月份"] == "2026-09" and r["营位类型"] == "临湖营位":
        total += Decimal(r["结算金额"])
print(json.dumps({"expected_number": float(total)}))
