import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders_march.csv"])))
orders = {r["order_id"] for r in rows}
print(json.dumps({"expected_number": len(orders)}))
