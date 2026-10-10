# DISTILL-CANARY-3ea9f5d2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/sept_orders.csv"]))
customers = {
    r["customer_id"]
    for r in rows
    if r["sales_channel"] == "Wholesale" and r["order_month"] == "2026-09"
}
print(json.dumps({"expected_number": len(customers)}))
