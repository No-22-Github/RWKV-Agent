# DISTILL-CANARY-3a546d9e : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/dispatch_2026-08.csv"])))
seen = set()
qty = {}
for r in rows:
    if r["单号"] in seen:
        continue
    seen.add(r["单号"])
    qty[r["型号"]] = qty.get(r["型号"], 0) + int(r["数量"])
top = max(qty, key=lambda k: qty[k])
print(json.dumps({"expected_number": float(qty[top])}))
