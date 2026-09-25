# DISTILL-CANARY-e2716b0c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["fluids/infusion_cards.csv"])))
order = [row for row in rows if row["order"] == "R-812"][0]
answer = float(order["volume_ml"]) * float(order["drop_factor_gtt_ml"]) / float(order["minutes"])
print(json.dumps({"expected_number": answer}))
