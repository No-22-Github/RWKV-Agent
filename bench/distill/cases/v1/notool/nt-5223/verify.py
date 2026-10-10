# DISTILL-CANARY-780c582e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["mains/reservoir_card.csv"])))
head = float(row["reservoir_level_m"]) - float(row["outlet_level_m"])
answer = head * float(row["kpa_per_m"])
print(json.dumps({"expected_number": answer}))
