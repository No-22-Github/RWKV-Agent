# DISTILL-CANARY-4c68a4cb : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]['运单/说明.md'].startswith('# 运单说明')
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == '运单,状态,运费', path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == '已签收':
            total += (int(whole) * 100 + int(frac)) if 'sum' == "sum" else 1
value = ("%d.%02d" % (total // 100, total % 100)) if 'sum' == "sum" else str(total)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(total // 100) + "." + "%02d" % (total % 100)] if 'sum' == "sum" else [value]}))
