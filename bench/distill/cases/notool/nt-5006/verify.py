# DISTILL-CANARY-4875fb36 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["roasts/roast_card.csv"]))
card = next(cards)
answer = int(card["total_roast_s"]) - int(card["first_crack_s"])
print(json.dumps({"expected_number": answer}))
