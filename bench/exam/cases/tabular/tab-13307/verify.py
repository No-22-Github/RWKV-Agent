# EXAM-CANARY-4c05f1a8 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.reader(io.StringIO(case["files"]["订单导出.csv"])))
assert rows[0] == ["订单号", "日期", "门店", "金额", "状态"]
print(json.dumps({"expected": round(sum(float(r[3]) for r in rows[1:] if r[1][:7] == "2026-09" and r[4] == "已退款"), 2)}))
