# DISTILL-CANARY-e5814c09 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/may_sales.csv"]))
total = 0.0
best_bags = ("", 0)
best_rev = ("", 0.0)
for r in rows:
    bags = int(r["袋数"])
    rev = float(r["销售额"])
    total += rev
    if bags > best_bags[1]:
        best_bags = (r["品种"], bags)
    if rev > best_rev[1]:
        best_rev = (r["品种"], rev)
assert best_bags[0] == best_rev[0]
print(json.dumps({
    "expected_number": round(total, 2),
    "turn_2_expected_contains": best_rev[0],
}))
