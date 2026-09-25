# DISTILL-CANARY-f3557a84 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["rigging/swl_card.csv"]))
card = next(cards)
safe_load = float(card["breaking_load_n"]) / float(card["factor"])
print(json.dumps({"expected_number": safe_load}))
