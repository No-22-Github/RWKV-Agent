# DISTILL-CANARY-d5a2946e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["links/loss_cards.csv"])))
answer = (float(card["km"]) * float(card["db_per_km"])
          + float(card["connectors"]) * float(card["connector_loss_db"])
          + float(card["splices"]) * float(card["splice_loss_db"]))
print(json.dumps({"expected_number": answer}))
