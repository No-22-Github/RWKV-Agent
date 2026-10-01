# DISTILL-CANARY-74a1b729 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/dispatch_2026-09.csv"]))
n = 0
for r in rows:
    if r["派车月份"] == "2026-09" and r["计费片区"] == "城北":
        n += 1
print(json.dumps({"expected_number": n}))
