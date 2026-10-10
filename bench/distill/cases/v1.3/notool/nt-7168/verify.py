# DISTILL-CANARY-9592a229 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["espresso/profiles.csv"]))
row = next(r for r in rows if r["basket"] == "双份粉碗")
dose = float(row["dose_g"])
num, den = row["ratio"].split(":")
print(json.dumps({"expected_number": dose * float(den) / float(num)}))
