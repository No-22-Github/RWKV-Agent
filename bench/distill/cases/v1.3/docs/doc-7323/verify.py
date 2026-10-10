# DISTILL-CANARY-5943ba97 : distillation case
import csv, io, json, re

case = json.load(open("case.json", encoding="utf-8"))
md = case["files"]["docs/差旅报销制度.md"]
rows = csv.DictReader(io.StringIO(case["files"]["docs/差旅住宿标准.csv"]))
caps = [float(r["住宿上限(元)"]) for r in rows
        if r["城市类别"] == "二类" and r["职级"] in ("主管", "经理")]
total = min(caps) * 2 if re.search(r"较低一档", md) else sum(caps)
if total == int(total):
    total = int(total)
print(json.dumps({"expected_number": total}))
