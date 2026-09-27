# DISTILL-CANARY-a87cafad : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["acquisitions_2026-06.csv"])))
count = sum(1 for r in rows
            if r["shelf"] == "Fiction" and float(r["price"]) < 8.0)
print(json.dumps({"expected_number": count}))
