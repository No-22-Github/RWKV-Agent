# DISTILL-CANARY-85a42a06 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/goods_in.csv"]))
pos = Decimal("0")
for r in rows:
    if r["月份"] == "2026-07":
        pos += Decimal(r["件数"])
rows = csv.DictReader(io.StringIO(case["files"]["data/goods_out.csv"]))
neg = Decimal("0")
for r in rows:
    if r["月份"] == "2026-07":
        neg += Decimal(r["件数"])
print(json.dumps({"expected_number": float(pos - neg)}))
