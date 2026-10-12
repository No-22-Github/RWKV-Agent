# DISTILL-CANARY-140fddd0 : distillation case
import json
case = json.load(open("case.json"))
js = case["files"]["工具/tally.js"]
assert "c[1] === '已发货'" in js and "toFixed(2)" in js
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "运单,状态,重量kg", path
    for row in rows[1:]:
        ident, status, w = row.split(",")
        if status == "已发货":
            cents += int(w.replace(".", ""))
value = "%d.%02d" % (cents // 100, cents % 100)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(cents // 100) + "." + "%02d" % (cents % 100)]}))
