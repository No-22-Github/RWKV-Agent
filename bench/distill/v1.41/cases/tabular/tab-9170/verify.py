# DISTILL-CANARY-a53dba85 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'orders/2026-07.csv': 77, 'orders/2026-08.csv': 85, 'orders/2026-09.csv': 94, 'orders/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["orders/README.md"].startswith("# Q3 orders")
counts = {}
months = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    months += 1
    rows = text.splitlines()
    assert rows[0] == "order_id,customer,status", path
    for row in rows[1:]:
        oid, customer, status = row.split(",")
        if status == "delivered":
            counts[customer] = counts.get(customer, 0) + 1
assert months == 3
ranked = sorted(counts.items(), key=lambda kv: -kv[1])
assert ranked[0][1] - ranked[1][1] >= 4
print(json.dumps({"expected_string": ranked[0][0]}))
