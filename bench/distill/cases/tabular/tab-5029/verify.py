# DISTILL-CANARY-8f03c96d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["landings_2026-08.csv"])))
sold = sum(int(r["value"]) for r in rows if r["sale_type"] == "open")
print(json.dumps({"expected_number": round(sold * 0.024, 2)}))
