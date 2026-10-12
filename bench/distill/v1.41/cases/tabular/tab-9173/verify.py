# DISTILL-CANARY-11c7d643 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'采购/清单.txt': 30, '采购/说明.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["采购/说明.md"].startswith("# 采购说明")
cents = 0
stopped = 0
for row in case["files"]["采购/清单.txt"].splitlines():
    if row.startswith("#"):
        stopped += 1
        continue
    name, qty, price = row.split(" ")
    whole, frac = price.split(".")
    assert len(frac) == 2, row
    cents += int(qty) * (int(whole) * 100 + int(frac))
assert stopped == 5
value = "%d.%02d" % (cents // 100, cents % 100)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(cents // 100) + "." + "%02d" % (cents % 100)]}))
