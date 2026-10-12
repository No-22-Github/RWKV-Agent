# DISTILL-CANARY-e3e0e5a2 : distillation case
import json
case = json.load(open("case.json"))
make = case["files"]["Makefile"]
assert make.startswith("DATA := 数据")
assert "$$2==\"已出库\"" in make
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == '出库单,状态,货值', path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == '已出库':
            cents += int(whole) * 100 + int(frac)
value = f"{cents // 100}.{cents % 100:02d}"
print(json.dumps({"expected_contains_any": [value, f"{cents // 100:,}.{cents % 100:02d}"]}))
