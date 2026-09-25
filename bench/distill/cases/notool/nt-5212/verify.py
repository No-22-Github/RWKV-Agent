# DISTILL-CANARY-e47a2d68 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["tariffs/erection-2026-09.csv"]))
price = next(r["saturday_gbp"] for r in rows if r["size"] == "12 m x 18 m")
print(json.dumps({"expected_number": float(price)}))
