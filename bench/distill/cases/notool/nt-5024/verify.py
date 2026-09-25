# DISTILL-CANARY-053fad90 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["milling/board_foot_card.csv"]))
card = next(cards)
cubic_in = (float(card["thickness_in"]) * float(card["width_in"])
            * float(card["length_ft"]) * 12.0)
print(json.dumps({"expected_number": cubic_in / 144.0}))
