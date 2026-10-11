# DISTILL-CANARY-efa0e967 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["导出/说明.md"].startswith("# 导出说明")
total = 0
direct = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "订单号,状态,渠道,备注", path
    if path.count("/") == 1:
        direct += 1
        for row in rows[1:]:
            f = row.split(",")
            assert len(f) == 4, row
            total += f[1] == "已退款"
assert direct == 6
print(json.dumps({"expected_number": total}))
