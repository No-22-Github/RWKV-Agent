# DISTILL-CANARY-58e2d19a : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["deliveries/september_week1.csv"]))
total = sum(int(r["dozens"]) for r in rows
            if r["branch"] == "Riverside" and r["item"] == "croissant")
print(json.dumps({"expected_number": total}))
