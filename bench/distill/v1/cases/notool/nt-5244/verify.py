# DISTILL-CANARY-751722d3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/speed_units.csv"])):
    rates[row[0]] = float(row[1])
runs = list(csv.DictReader(io.StringIO(files["runs/passage_log_7719.tsv"]), delimiter="\t"))
run = [row for row in runs if row["run"] == "SR-7719"][0]
print(json.dumps({
    "expected_number": float(run["speed_knots"]) * rates["kilometre_per_hour_per_knot"]
}))
