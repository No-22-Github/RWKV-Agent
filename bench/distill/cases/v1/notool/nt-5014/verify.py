# DISTILL-CANARY-698bb58f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["intake/bushel_card.csv"]))
card = next(cards)
bushels = float(card["net_lb"]) / float(card["test_weight_lb_per_bu"])
print(json.dumps({"expected_number": bushels}))
