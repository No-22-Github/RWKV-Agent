# EXAM-CANARY-e82fd28c : exam gap-fill case
import csv, io, json
from decimal import Decimal, ROUND_HALF_UP
case = json.load(open("case.json", encoding="utf-8"))
tot = {}
for r in csv.DictReader(io.StringIO(case["files"]["expenses.csv"])):
    tot[r["dept"]] = tot.get(r["dept"], Decimal(0)) + Decimal(r["amount"])
g = sum(tot.values())
out = "department,total,share\n"
for d, t in sorted(tot.items(), key=lambda x: -x[1]):
    out += "%s,%.2f,%s%%\n" % (d, t, (t * 100 / g).quantize(Decimal("0.1"), ROUND_HALF_UP))
print(json.dumps({"files": {"summary.csv": out}}))
