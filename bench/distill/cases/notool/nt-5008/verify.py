# DISTILL-CANARY-acd84fa0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["loom/sley_card.csv"]))
card = next(cards)
sett = int(card["dents_per_inch"]) * int(card["ends_per_dent"])
ends = sett * int(card["width_in"])
print(json.dumps({"expected_number": ends}))
