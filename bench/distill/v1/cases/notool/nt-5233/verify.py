# DISTILL-CANARY-3fc4d01e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["runs/leg_cards.csv"])))
answer = float(row["payload_t"]) * float(row["distance_km"])
print(json.dumps({"expected_number": answer}))
