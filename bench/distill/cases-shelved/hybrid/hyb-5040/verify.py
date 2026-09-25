# DISTILL-CANARY-86d213ac : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["weighbridge/tip-book-september.csv"])))
gross = sum(int(row["gross_kg"]) for row in rows)
tare = sum(int(row["tare_kg"]) for row in rows)
net = gross - tare
if tare == 0 or net >= gross:
    raise SystemExit("the empty weight must come off the loaded weight")
print(json.dumps({"expected_number": net}))
