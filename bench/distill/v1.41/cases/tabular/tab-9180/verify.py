# DISTILL-CANARY-1e25d51f : distillation case
import json
case = json.load(open("case.json"))
LINES = {'开销.txt': 6}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
rows = case["files"]["开销.txt"].splitlines()
assert rows[0] == "# 十月开销"
assert rows[-1].startswith("# 上月合计")
total = 0.0
n = 0
for row in rows:
    if row.startswith("#"):
        continue
    total += float(row.split(" ")[1])
    n += 1
assert n == 4
print(json.dumps({"expected_contains_any": ["%d" % total, "{:,}".format(int(total))]}))
