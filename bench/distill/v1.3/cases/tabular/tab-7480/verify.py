# DISTILL-CANARY-87af913c : distillation case
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

rows = list(csv.DictReader(io.StringIO(case["files"]["data/shifts_2026-09.csv"])))
HOLIDAYS = {"2026-09-26", "2026-09-27"}
pay = Decimal("0")
for r in rows:
    mult = Decimal("3") if _iso(r["日期"]) in HOLIDAYS else Decimal("1.5")
    pay += Decimal(r["加班小时"]) * Decimal("24") * mult
print(json.dumps({"expected_number": float(pay)}))
