# DISTILL-CANARY-5e826f4c : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]['报名/说明.md'].startswith('# 报名说明')
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == '学号,状态,学费', path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == '已缴费':
            total += (int(whole) * 100 + int(frac)) if 'count' == "sum" else 1
value = ("%d.%02d" % (total // 100, total % 100)) if 'count' == "sum" else str(total)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(total // 100) + "." + "%02d" % (total % 100)] if 'count' == "sum" else [value]}))
