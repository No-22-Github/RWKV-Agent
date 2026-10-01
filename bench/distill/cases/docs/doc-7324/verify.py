# DISTILL-CANARY-ca4558fe : distillation case
import csv, io, json, re
from datetime import date, timedelta

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/样品登记.csv"]))
text = case["files"]["docs/留存规定.md"]
row = next(r for r in rows if r["样品编号"] == "CZ-S-0412")
if row["加急"] == "是":
    days = int(re.search(r"加急[^。\n]*?留存\s*(\d+)\s*天", text).group(1))
else:
    days = int(re.search(row["类别"] + r"类[^。\n]*?留存\s*(\d+)\s*天", text).group(1))
s = row["收样日期"].strip()
if "/" in s:
    m, d, y = s.split("/")
    dt = date(int(y), int(m), int(d))
elif "." in s:
    y, m, d = s.split(".")
    dt = date(int(y), int(m), int(d))
else:
    y, m, d = s.split("-")
    dt = date(int(y), int(m), int(d))
print(json.dumps({"expected_contains_any": [(dt + timedelta(days=days)).isoformat()]}))
