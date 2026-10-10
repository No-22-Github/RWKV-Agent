# DISTILL-CANARY-f0a31b54 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/liushui-2026-08.csv"]))
total = Decimal("0")
n_refund = 0
for r in rows:
    if r["类型"] == "冲正":
        total -= Decimal(r["金额"])
        n_refund += 1
    elif r["类型"] == "销售":
        total += Decimal(r["金额"])
if n_refund < 1:
    raise SystemExit("fixture guard failed: the refund rows are gone")
print(json.dumps({"expected_number": float(total)}))
