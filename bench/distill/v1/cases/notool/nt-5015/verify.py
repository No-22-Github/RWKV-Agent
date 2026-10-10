# DISTILL-CANARY-270b400b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["stock/paper_card.csv"]))
card = next(cards)
area_m2 = float(card["width_mm"]) / 1000.0 * float(card["height_mm"]) / 1000.0
grams = area_m2 * float(card["gsm"])
print(json.dumps({"expected_number": grams}))
