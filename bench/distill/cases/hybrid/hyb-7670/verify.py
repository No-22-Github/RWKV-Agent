# DISTILL-CANARY-428f8cbf : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["销售台账.csv"]))
total = 0.0
for r in rows:
    if str(r["客户"]).strip() == "华达商贸" and str(r["日期"]).strip().startswith("2026-08"):
        total += float(str(r["金额"]).strip())
print(json.dumps({"expected_number": total}))
