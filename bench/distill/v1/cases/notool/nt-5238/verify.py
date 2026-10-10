# DISTILL-CANARY-4c94db65 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["stock/board_reams.csv"])))
sheet_mass_g = (float(row["sheet_width_m"]) * float(row["sheet_length_m"])
                 * float(row["grammage_g_m2"]))
answer = sheet_mass_g * float(row["sheets_per_ream"]) / 1000.0
print(json.dumps({"expected_number": answer}))
