# EXAM-CANARY-a85e2f60 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.reader(io.StringIO(case["files"]["销售明细.csv"])))
assert rows[0] == ["日期", "区域", "商品", "数量", "单价", "类型", "门店"]
print(json.dumps({"expected": round(sum(int(r[3]) * float(r[4]) for r in rows[1:] if r[1] == "华东" and r[0][:7] == "2026-08" and r[5] == "销售"), 2)}))
