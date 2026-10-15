# EXAM-CANARY-aac8a124 : exam gap-fill case
import json
from decimal import Decimal

case = json.load(open("case.json", encoding="utf-8"))
qty, rev = {}, {}
for line in case["files"]["sales.csv"].splitlines()[1:]:
    _day, item, n, price = line.split(",")
    qty[item] = qty.get(item, 0) + int(n)
    rev[item] = rev.get(item, Decimal(0)) + int(n) * Decimal(price)
best = max(qty, key=qty.get)
assert sorted(qty.values())[-1] > sorted(qty.values())[-2]
print(json.dumps({"expected_number": float(rev[best])}))
