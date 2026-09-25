# DISTILL-CANARY-6a73b1c4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["batteries/site_cards.csv"])))
usable_wh = (float(card["capacity_ah"]) * float(card["bank_v"])
             * float(card["discharge_pct"]) / 100.0)
answer = usable_wh / 1000.0 / float(card["daily_load_kwh"])
print(json.dumps({"expected_number": answer}))
