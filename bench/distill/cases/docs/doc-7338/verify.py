# DISTILL-CANARY-e0a06af8 : distillation case
import csv, io, json
from datetime import date

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["官网页面清单.csv"]))

def parse(s):
    s = s.strip()
    if "/" in s:
        m, d, y = s.split("/")
        return date(int(y), int(m), int(d))
    if "." in s:
        y, m, d = s.split(".")
        return date(int(y), int(m), int(d))
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))

missing = [r["链接路径"] for r in rows
           if parse(r["上线日期"]).year == 2026 and parse(r["上线日期"]).month == 4
           and r["链接路径"] not in case["files"]]
print(json.dumps({"expected_number": len(missing)}))
