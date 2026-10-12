# DISTILL-CANARY-6db9550b : distillation case
import json
case = json.load(open("case.json"))
make = case["files"]["Makefile"]
assert make.startswith("DATA := 数据")
assert "$$2==\"已发货\"" in make
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "订单,状态,金额", path
    for row in rows[1:]:
        order, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == "已发货":
            cents += int(whole) * 100 + int(frac)
value = f"{cents // 100}.{cents % 100:02d}"
print(json.dumps({"expected_contains_any": [value, f"{cents // 100:,}.{cents % 100:02d}"]}))
