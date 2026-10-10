# DISTILL-CANARY-7c41ba92 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["hive_harvest.csv"])))
print(json.dumps({"expected_number": round(sum(float(r["honey_kg"]) for r in rows), 2)}))
