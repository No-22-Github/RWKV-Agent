# DISTILL-CANARY-10860487 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["待办工单.csv"]))
n = sum(1 for r in rows if r["状态"] == "待处理")
print(json.dumps({"expected_number": n}))
