# DISTILL-CANARY-5a572ec2 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/author_sales_2026-08.csv"])))
sums = {}
for r in rows:
    sums[r["作者"]] = sums.get(r["作者"], Decimal("0")) + Decimal(r["金额"])
top = max(sums, key=lambda k: sums[k])
print(json.dumps({"expected_string": top}))
