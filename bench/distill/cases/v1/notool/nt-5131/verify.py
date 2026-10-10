# DISTILL-CANARY-c93e8057 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["batteries/relay_cards.csv"])))
usable_wh = (float(card["capacity_ah"]) * float(card["bus_v"])
             * float(card["discharge_pct"]) / 100.0)
answer = usable_wh / float(card["load_w"])
print(json.dumps({"expected_number": answer}))
