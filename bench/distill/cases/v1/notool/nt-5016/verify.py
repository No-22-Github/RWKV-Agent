# DISTILL-CANARY-b89b9c0b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["vault/carton_card.csv"]))
card = next(cards)
shelving = float(card["linear_ft_each"]) * float(card["count"])
print(json.dumps({"expected_number": shelving}))
