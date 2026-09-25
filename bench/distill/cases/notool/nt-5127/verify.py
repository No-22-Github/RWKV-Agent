# DISTILL-CANARY-7b3f0a9d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["pool/heating_card.csv"])))
answer = (float(card["water_kg"]) * float(card["spec_heat_kj_kg_k"])
          * (float(card["end_c"]) - float(card["start_c"])))
print(json.dumps({"expected_number": answer}))
