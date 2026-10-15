# EXAM-CANARY-75cbc080 : exam gap-fill case
import json
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

case = json.load(open("case.json", encoding="utf-8"))
seen = set()
agg = {}
for line in case["files"]["orders.csv"].splitlines()[1:]:
    if line in seen:
        continue
    seen.add(line)
    oid, city, amt, _ = line.split(",")
    agg.setdefault(city, []).append(Decimal(amt))
out = ["| 城市 | 订单数 | 平均客单价 |", "| --- | --- | --- |"]
for city in sorted(agg):
    v = agg[city]
    avg = (sum(v) / len(v)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    out.append("| %s | %d | %s |" % (city, len(v), avg))
print(json.dumps({"files": {"report.md": "\n".join(out) + "\n"}}, ensure_ascii=False))
