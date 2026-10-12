# DISTILL-CANARY-a3fa430a : distillation case
import json
case = json.load(open("case.json"))
rows = case["files"]['订单日志/order.log'].splitlines()
readme = case["files"]['订单日志/说明.md']
assert str(len(rows)) in readme
last = None
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 5 and parts[3].startswith('订单='), row
    if parts[2] == '库存不足':
        last = parts[3][len('订单='):]
assert last
print(json.dumps({"expected_string": last}))
