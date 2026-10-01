# DISTILL-CANARY-07e328f0 : distillation case
import csv, io, json, re
from datetime import date

case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["清洁标准.md"]
ok_grades = [g.strip() for g in re.search(r"（([^（）]*)视为达标", text).group(1).split("、")]
ph_max = float(re.search(r"pH\s*不高于\s*([\d.]+)", text).group(1))
rows = csv.DictReader(io.StringIO(case["files"]["洗涤批次对账.csv"]))

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

n = 0
for r in rows:
    dt = parse(r["送洗日期"])
    if dt.year == 2026 and dt.month == 9:
        if r["洁净度"] not in ok_grades or float(r["pH"]) > ph_max:
            n += 1
print(json.dumps({"expected_number": n}))
