# DISTILL-CANARY-3651dcdc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["pantry/deliveries.csv"]))
barrels = next(int(r["barrels"]) for r in rows if r["week"] == "2026-W36")
print(json.dumps({"expected_number": barrels * 18.9}))
