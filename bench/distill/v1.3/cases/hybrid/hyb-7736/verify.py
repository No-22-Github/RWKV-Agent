# DISTILL-CANARY-b8183f47 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["inventory/stock.csv"]))
qty = next(int(r["库存包数"]) for r in rows
           if r["品名"] == "复印纸" and r["规格"] == "70g" and r["sku"] == "ZY-A4-70")
print(json.dumps({"expected_number": qty}))
