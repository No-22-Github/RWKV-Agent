# DISTILL-CANARY-6274e543 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["体测复检名单.csv"]))
members = [r["会员号"] for r in rows if float(r["体脂率(%)"]) > 22 and r["状态"] == "未预约"]
print(json.dumps({"expected_contains_any": members}))
