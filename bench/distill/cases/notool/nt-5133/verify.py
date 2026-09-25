# DISTILL-CANARY-9f05d683 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["stores/dilution_cards.csv"])))
final_l = float(card["concentrate_l"]) * float(card["strength_pct"]) / float(card["target_pct"])
answer = final_l - float(card["concentrate_l"])
print(json.dumps({"expected_number": answer}))
