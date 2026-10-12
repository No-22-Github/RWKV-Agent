# DISTILL-CANARY-18d361b7 : distillation case
import json
case = json.load(open("case.json"))
jf = case["files"]["justfile"]
assert "stock:" in jf and "$2==\"已入库\"" in jf
n = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "批次,状态,数量", path
    for row in rows[1:]:
        ident, status, qty = row.split(",")
        if status == "已入库":
            n += int(qty)
print(json.dumps({"expected_contains_any": [str(n), "{:,}".format(n)]}))
