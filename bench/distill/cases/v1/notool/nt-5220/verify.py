# DISTILL-CANARY-44dc68ee : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["timber/pack_sheets.csv"])))
one_board = float(row["thickness_in"]) * float(row["width_in"]) * float(row["length_ft"]) / 12.0
answer = one_board * float(row["pieces"])
print(json.dumps({"expected_number": answer}))
