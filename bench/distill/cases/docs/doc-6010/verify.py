# DISTILL-CANARY-2378bc1b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["warranty/cover.csv"])))

# README.md: the sheet covers manufacture faults only; accidental damage is
# sold separately and never appears on the cover sheet.
value = "UNKNOWN"
for row in rows:
    if row["model"].strip().lower() == "dishwasher":
        if "accidental_damage_years" in row:
            value = row["accidental_damage_years"].strip()
        break

print(json.dumps({"expected_string": value}))
