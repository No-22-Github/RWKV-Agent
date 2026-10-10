# DISTILL-CANARY-d4c92870 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["fleece_intake_2026-08.csv"])))
seen = set()
total = 0.0
for row in rows:
    if row["station"] != "Fellgate" or row["lot_id"] in seen:
        continue
    seen.add(row["lot_id"])
    total += float(row["weight_kg"])
print(json.dumps({"expected_number": round(total, 1)}))
