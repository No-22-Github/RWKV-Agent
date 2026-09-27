# DISTILL-CANARY-63e6facc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["warranty/cover.csv"]))

# README.md: one row per model with the parts and labour terms in years.
value = None
for row in rows:
    if row["model"].strip().lower() == "fridge freezer":
        value = float(row["labour_years"])
        break

print(json.dumps({"expected_number": value}))
