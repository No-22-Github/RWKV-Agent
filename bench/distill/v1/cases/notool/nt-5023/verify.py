# DISTILL-CANARY-2b8999bc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["plans/scale_card.csv"]))
card = next(cards)
ground_cm = float(card["measured_cm"]) * float(card["scale_denominator"])
print(json.dumps({"expected_number": ground_cm / 100000.0}))
