# DISTILL-CANARY-4b1f3f85 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["sewing/signature_card.csv"]))
card = next(cards)
pages = int(card["signatures"]) * int(card["leaves_per_signature"]) * 2
print(json.dumps({"expected_number": pages}))
