# DISTILL-CANARY-f1f4f8c5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["batches/sponge_cards.csv"])))
answer = float(row["water_kg"]) / (float(row["hydration_pct"]) / 100.0)
print(json.dumps({"expected_number": answer}))
