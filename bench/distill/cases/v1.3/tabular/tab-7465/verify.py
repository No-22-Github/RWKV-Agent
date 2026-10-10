# DISTILL-CANARY-2e1faa82 : distillation case
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

rows = list(csv.DictReader(io.StringIO(case["files"]["data/bookings_2026-09.csv"])))
seen = set()
n = 0
for r in rows:
    if r["预订单号"] in seen:
        continue
    if not _iso(r["入住日期"]).startswith("2026-09"):
        continue
    seen.add(r["预订单号"])
    n += 1
print(json.dumps({"expected_number": float(n)}))
