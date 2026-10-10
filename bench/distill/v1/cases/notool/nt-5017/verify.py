# DISTILL-CANARY-95c06d8b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["kitchen/yield_card.csv"]))
card = next(cards)
usable = float(card["whole_kg"]) * float(card["yield_pct"]) / 100.0
print(json.dumps({"expected_number": usable}))
