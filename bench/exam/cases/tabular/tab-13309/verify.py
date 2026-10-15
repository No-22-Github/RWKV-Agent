# EXAM-CANARY-2d7a8e51 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.reader(io.StringIO(case["files"]["工单导出.csv"])))
assert rows[0][0] == "工单号"
print(json.dumps({"expected": sum(1 for r in rows[1:] if r[1][:7] == "2026-09" and r[3] == "P1" and r[5] == "已关闭" and int(r[4]) > 48)}))
