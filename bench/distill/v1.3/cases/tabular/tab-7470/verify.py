# DISTILL-CANARY-b6865bbb : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/signups_2026-09.csv"])))
sums = {}
for r in rows:
    sums[r["套餐"]] = sums.get(r["套餐"], 0) + int(r["人数"])
top = max(sums, key=lambda k: sums[k])
print(json.dumps({"expected_contains_any": [top]}))
