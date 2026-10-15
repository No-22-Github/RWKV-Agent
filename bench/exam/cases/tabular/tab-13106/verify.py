# EXAM-CANARY-915491aa : exam gap-fill case
import json
from decimal import Decimal

case = json.load(open("case.json", encoding="utf-8"))
tot = {}
for line in case["files"]["报销.csv"].splitlines()[1:]:
    day, dep, _what, net, tax = line.split(",")
    if day.startswith("2026-09"):
        tot[dep] = tot.get(dep, Decimal(0)) + Decimal(net) + Decimal(tax)
out = "部门,金额\n"
for dep, v in sorted(tot.items(), key=lambda kv: (-kv[1], kv[0])):
    out += "%s,%s\n" % (dep, v.quantize(Decimal("0.01")))
print(json.dumps({"files": {"汇总/9月报销.csv": out}}, ensure_ascii=False))
