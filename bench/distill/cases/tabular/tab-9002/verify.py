# DISTILL-CANARY-0ce2851f : distillation case
import json
case = json.load(open("case.json"))
cents = 0
for path, text in case["files"].items():
    if not path.endswith("orders.csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "order_id,sku,status,amount_usd", path
    for row in rows[1:]:
        oid, sku, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == "refunded" and sku.startswith("KX-"):
            cents += int(whole) * 100 + int(frac)
print(json.dumps({"expected_number": cents / 100}))
