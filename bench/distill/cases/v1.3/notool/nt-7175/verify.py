# DISTILL-CANARY-15a37b34 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["shop/connectors.csv"]))
row = next(r for r in rows if r["type"] == "大二芯插头")
print(json.dumps({"expected_number": float(row["diameter_mm"]) / 25.4}))
