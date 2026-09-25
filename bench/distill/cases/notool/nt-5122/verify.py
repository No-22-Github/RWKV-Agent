# DISTILL-CANARY-f83a2c41 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["tanks/density_cards.csv"])))
answer = float(card["biomass_kg"]) / float(card["volume_m3"])
print(json.dumps({"expected_number": answer}))
