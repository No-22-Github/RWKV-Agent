# DISTILL-CANARY-5df69db1 : distillation case
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

rows = list(csv.DictReader(io.StringIO(case["files"]["data/waimai_2026-09.csv"])))
n = sum(1 for r in rows if "2026-09-01" <= _iso(r["日期"]) <= "2026-09-10")
print(json.dumps({"expected_number": float(n)}))
