# DISTILL-CANARY-cdbcc8fa : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["值班登记.csv"]))
by_date = {}
order = []
for r in rows:
    d = r["日期"]
    if d not in by_date:
        by_date[d] = {}
        order.append(d)
    by_date[d][r["班次"]] = r["员工"]
lines = ["# 下周值班通知", ""]
for d in order:
    lines.append("{}：早班 {}，晚班 {}".format(d, by_date[d]["早班"], by_date[d]["晚班"]))
content = "\n".join(lines) + "\n"
print(json.dumps({"files": {"下周值班通知.md": content}}))
