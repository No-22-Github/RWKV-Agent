# DISTILL-CANARY-0f9b23d5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["tides/beacon_reach_card.csv"])))
answer = int(card["twelfths_remaining"]) / 12.0 * float(card["range_m"])
print(json.dumps({"expected_number": answer}))
