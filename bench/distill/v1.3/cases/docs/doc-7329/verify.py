# DISTILL-CANARY-22d3f764 : distillation case
import csv, io, json
from datetime import date

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/网关SDK更新记录.tsv"]), delimiter="\t")

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

kept = [r for r in rows if r["通道"] == "正式"]
latest = max(kept, key=lambda r: parse(r["发布日期"]))
print(json.dumps({"expected_contains_any": [latest["版本号"]]}))
