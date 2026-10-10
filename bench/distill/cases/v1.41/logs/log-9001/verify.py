# DISTILL-CANARY-36362099 : distillation case
import json
case = json.load(open("case.json"))
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "时间,级别,服务,事件", path
    for row in rows[1:]:
        assert row.count(",") == 3, row
        total += row.split(",")[3] == "支付超时"
print(json.dumps({"expected_number": total}))
