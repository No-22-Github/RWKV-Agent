# DISTILL-CANARY-1d60e59b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["sheds/conversion_cards.csv"])))
answer = float(card["feed_kg"]) / float(card["liveweight_gain_kg"])
print(json.dumps({"expected_number": answer}))
