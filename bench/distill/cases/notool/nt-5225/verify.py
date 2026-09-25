# DISTILL-CANARY-020067b6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["batches/dough_cards.csv"])))
answer = float(row["flour_kg"]) * float(row["hydration_pct"]) / 100.0
print(json.dumps({"expected_number": answer}))
