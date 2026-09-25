# DISTILL-CANARY-181554a7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["press/imposition_card.csv"]))
card = next(cards)
pages = (int(card["sheets"]) * int(card["pages_per_side"])
         * int(card["sides_printed"]))
print(json.dumps({"expected_number": pages}))
