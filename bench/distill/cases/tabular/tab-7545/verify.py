# DISTILL-CANARY-01de4fc4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/workorders_2026-09.csv"]))
n = 0
for r in rows:
    if r["工单月份"] == "2026-09" and r["服务片区"] == "城东":
        n += 1
print(json.dumps({"expected_number": n}))
