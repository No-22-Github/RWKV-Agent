# DISTILL-CANARY-393cb01c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["records/检修记录-2026-09.csv"]))
lines = [",".join([r["日期"], r["楼栋"], r["电梯"], r["项目"], r["结果"]]) for r in rows]
print(json.dumps({"files": {"notices/电梯检修通知.md": "\n".join(lines) + "\n"}}))
