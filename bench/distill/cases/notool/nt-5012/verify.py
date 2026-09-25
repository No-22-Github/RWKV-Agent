# DISTILL-CANARY-e00ba5fa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["houses/dif_card.csv"]))
card = next(cards)
dif = float(card["day_c"]) - float(card["night_c"])
print(json.dumps({"expected_number": dif}))
