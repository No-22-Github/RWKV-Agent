# DISTILL-CANARY-f444b350 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["runs/trip_cards.csv"])))
answer = float(row["loaded_km"]) * float(row["payload_t"])
print(json.dumps({"expected_number": answer}))
