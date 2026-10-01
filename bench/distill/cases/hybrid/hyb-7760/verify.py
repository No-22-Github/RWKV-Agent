# DISTILL-CANARY-5a19784a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["rates/房价-2026-09.csv"]))
lines = [",".join([r["日期"], r["房型"], r["门市价"], r["渠道价"]]) for r in rows if r["日期"] == "2026-10-01"]
print(json.dumps({"files": {"政策/调价公告.md": "\n".join(lines) + "\n"}}))
