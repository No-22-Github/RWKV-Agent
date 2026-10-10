# DISTILL-CANARY-850e9f7d : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/shipments_2026-08.csv"])))
seen = set()
qty = 0
for r in rows:
    if r["出库单号"] in seen:
        continue
    seen.add(r["出库单号"])
    if r["品类"] == "古筝":
        qty += int(r["数量"])
print(json.dumps({"expected_number": float(qty)}))
