# DISTILL-CANARY-41d7ba2e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["vat/strength_cards.csv"])))
final_l = float(card["current_l"]) * float(card["current_pct"]) / float(card["target_pct"])
answer = final_l - float(card["current_l"])
print(json.dumps({"expected_number": answer}))
