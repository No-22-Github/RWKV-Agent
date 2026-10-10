# DISTILL-CANARY-57be9014 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["runs/fuel_cards.csv"])))
answer = float(card["fuel_l"]) / float(card["distance_km"]) * 100.0
print(json.dumps({"expected_number": answer}))
