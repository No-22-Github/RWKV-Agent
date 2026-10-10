# DISTILL-CANARY-c4097da6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["blocks/fertiliser_cards.csv"])))
product = float(card["rate_kg_ha"]) * float(card["area_ha"])
answer = product * float(card["analysis_n_pct"]) / 100.0
print(json.dumps({"expected_number": answer}))
