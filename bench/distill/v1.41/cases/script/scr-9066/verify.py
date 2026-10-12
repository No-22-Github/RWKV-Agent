# DISTILL-CANARY-5d59d494 : distillation case
import json
case = json.load(open("case.json"))
make = case["files"]["Makefile"]
assert make.startswith("DATA := 数据")
assert "$$2==\"已审批\"" in make
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == '工单,状态,工时', path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == '已审批':
            cents += int(whole) * 100 + int(frac)
value = f"{cents // 100}.{cents % 100:02d}"
print(json.dumps({"expected_contains_any": [value, f"{cents // 100:,}.{cents % 100:02d}"]}))
