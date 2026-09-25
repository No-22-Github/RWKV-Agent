# DISTILL-CANARY-3e9a07b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/shipments_2026-08.csv"]))
orders = {r["order_ref"] for r in rows if r["destination_country"] == "Canada" and r["ship_date"].startswith("2026-08")}
print(json.dumps({"expected_number": len(orders)}))
