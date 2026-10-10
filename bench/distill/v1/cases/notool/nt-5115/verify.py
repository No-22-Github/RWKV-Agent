# DISTILL-CANARY-6c1d47ae : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["tides/skerry_cove_card.csv"])))
answer = int(card["cumulative_twelfths"]) / 12.0 * float(card["range_m"])
print(json.dumps({"expected_number": answer}))
