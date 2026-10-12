# DISTILL-CANARY-271badbb : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]['invoices/README.md'].startswith('# Invoice exports')
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == 'invoice,state,amount', path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == 'paid':
            total += (int(whole) * 100 + int(frac)) if 'sum' == "sum" else 1
value = ("%d.%02d" % (total // 100, total % 100)) if 'sum' == "sum" else str(total)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(total // 100) + "." + "%02d" % (total % 100)] if 'sum' == "sum" else [value]}))
