# DISTILL-CANARY-b31e9316 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["rooms/depression_card.csv"]))
card = next(cards)
depression = float(card["dry_bulb_c"]) - float(card["wet_bulb_c"])
print(json.dumps({"expected_number": depression}))
