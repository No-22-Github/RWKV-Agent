# DISTILL-CANARY-a896581a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["timesheets/工时表.csv"]))
total = 0.0
for r in rows:
    if r["测量员"] == "高志远" and r["项目"] == "青峦水库":
        total += float(r["工时"]) * float(r["时薪"])
print(json.dumps({"expected_number": round(total, 2)}))
