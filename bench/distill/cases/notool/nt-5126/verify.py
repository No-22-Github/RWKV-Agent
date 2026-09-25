# DISTILL-CANARY-a16c5e82 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["rooms/chill_cards.csv"])))
energy = (float(card["product_kg"]) * float(card["spec_heat_kj_kg_k"])
          * (float(card["start_c"]) - float(card["end_c"])))
answer = energy / float(card["pull_down_s"])
print(json.dumps({"expected_number": answer}))
