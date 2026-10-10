# DISTILL-CANARY-2224dc2f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["brew/plato_card.csv"]))
card = next(cards)
extract = float(card["mash_mass_kg"]) * float(card["plato"]) / 100.0
print(json.dumps({"expected_number": extract}))
