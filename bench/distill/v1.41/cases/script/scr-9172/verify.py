# DISTILL-CANARY-993d031b : distillation case
import json
case = json.load(open("case.json"))
LINES = {'data/orders-east.csv': 150, 'data/orders-west.csv': 148, 'tools/slow_orders.py': 9}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
script = case["files"]["tools/slow_orders.py"]
assert "row['status'] == 'delivered' and int(row['delay_days']) > 3" in script
assert script.startswith("import csv, glob")
n = 0
shards = 0
for path, text in case["files"].items():
    if not path.startswith("data/orders-"):
        continue
    shards += 1
    rows = text.splitlines()
    assert rows[0] == "order_id,region,status,delay_days", path
    for row in rows[1:]:
        oid, region, status, delay = row.split(",")
        n += status == "delivered" and int(delay) > 3
assert shards == 2
print(json.dumps({"expected_number": n}))
