# DISTILL-CANARY-3b7f0d52 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/march_orders.csv"]))
orders = {}
for r in rows:
    if r["channel"] == "wholesale" and r["date"].startswith("2026-03"):
        orders[r["order_id"]] = orders.get(r["order_id"], 0) + int(r["bags"])
print(json.dumps({
    "expected_number": len(orders),
    "turn_2_expected_number": sum(orders.values()),
}))
