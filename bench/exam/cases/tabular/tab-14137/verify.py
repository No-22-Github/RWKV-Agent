# EXAM-CANARY-9f86adfb : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
tot = {}
for line in case["files"]["sales/orders.csv"].splitlines()[1:]:
    _oid, region, status, amount = line.split(",")
    if status == "paid":
        tot[region] = tot.get(region, 0) + int(amount)
print(json.dumps({"expected_contains_all": [str(v) for k, v in sorted(tot.items())]}))
