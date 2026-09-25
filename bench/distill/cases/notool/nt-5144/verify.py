# DISTILL-CANARY-06f60c33 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
bars = list(csv.DictReader(io.StringIO(files["vault/bars_2607.tsv"]), delimiter="\t"))
ounces = float(next(row["fine_ounces"] for row in bars if row["bar"] == "LB-2607"))
units = {}
for row in csv.reader(io.StringIO(files["standards/assay_weights.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({"expected_number": ounces * units["troy_ounce_to_grain"]}))
