# DISTILL-CANARY-6ea35491 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["stock/pallet_cards.csv"])))
reams = float(row["reams_per_bundle"]) * float(row["bundles_per_pallet"])
answer = reams * float(row["sheets_per_ream"])
print(json.dumps({"expected_number": answer}))
