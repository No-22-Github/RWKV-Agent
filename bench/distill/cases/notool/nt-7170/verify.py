# DISTILL-CANARY-06dcf150 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/curtain_order.csv"]))
row = next(r for r in rows if r["order"] == "窗帘-王宅")
print(json.dumps({"expected_number": float(row["yards"]) * 0.9144}))
