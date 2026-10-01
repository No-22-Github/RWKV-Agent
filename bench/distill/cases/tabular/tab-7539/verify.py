# DISTILL-CANARY-457e4e00 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/returns_2026-09.csv"]))
items = set()
for r in rows:
    if r["return_month"] == "2026-09" and r["branch"] == "East":
        items.add(r["item_code"])
print(json.dumps({"expected_number": len(items)}))
