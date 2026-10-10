# DISTILL-CANARY-c8e49c56 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
def _iso(s):
    if "-" in s:
        return s
    dd, mm, yy = s.split("/")
    return yy + "-" + mm + "-" + dd

rows = list(csv.DictReader(io.StringIO(case["files"]["data/dispatch_log_2026-09.csv"])))
sums = {}
for r in rows:
    d = _iso(r["日期"])
    if not ("2026-09-01" <= d <= "2026-09-15"):
        continue
    sums[r["工地"]] = sums.get(r["工地"], 0.0) + float(r["吨数"])
top = max(sums, key=lambda k: sums[k])
print(json.dumps({"expected_number": float(round(sums[top], 2))}))
