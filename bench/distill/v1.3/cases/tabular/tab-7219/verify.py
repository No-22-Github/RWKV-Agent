# DISTILL-CANARY-5d267c19 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/jiaoyi-2026-09.csv"]))
total = Decimal("0")
n = 0
for r in rows:
    if r["客户"] == "广茂建材":
        total += Decimal(r["金额"])
        n += 1
if n < 1:
    raise SystemExit("fixture guard failed: the target customer rows are gone")
print(json.dumps({"expected_number": float(total)}))
