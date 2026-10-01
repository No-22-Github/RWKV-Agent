# DISTILL-CANARY-854d3056 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/wholesale_2026-09.csv"])))
sums = {}
for r in rows:
    sums[r["客户"]] = sums.get(r["客户"], Decimal("0")) + Decimal(r["金额"])
ranked = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)
second = ranked[1][0]
print(json.dumps({"expected_string": second}))
