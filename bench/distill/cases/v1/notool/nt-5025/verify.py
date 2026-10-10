# DISTILL-CANARY-f54325a1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["builds/gear_card.csv"]))
card = next(cards)
gears = (float(card["wheel_diameter_in"])
         * float(card["chainring_teeth"]) / float(card["sprocket_teeth"]))
print(json.dumps({"expected_number": gears}))
