# DISTILL-CANARY-6c41d2f9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/exports-2026Q2.csv"]))
seen = set()
total = 0
for r in rows:
    if r["物料"] == "垫圈" and r["出库日期"].startswith("2026-04"):
        if r["单号"] in seen:
            continue
        seen.add(r["单号"])
        total += int(r["数量"])
print(json.dumps({"expected_number": total}))
