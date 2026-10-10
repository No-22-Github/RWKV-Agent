# DISTILL-CANARY-94c8f3a7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["fluids/order_cards.csv"])))
order = [row for row in rows if row["order"] == "D-247"][0]
answer = float(order["volume_ml"]) * float(order["drop_factor_gtt_ml"]) / float(order["minutes"])
print(json.dumps({"expected_number": answer}))
