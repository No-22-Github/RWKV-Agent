# DISTILL-CANARY-12d24ac6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
gusts = list(csv.DictReader(io.StringIO(files["turbines/gust_log_8834.tsv"]), delimiter="\t"))
peak = float(next(row["peak_gust_metres_per_second"] for row in gusts if row["turbine"] == "RW-07"))
units = {}
for row in csv.reader(io.StringIO(files["standards/wind_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": peak * units["metre_per_second_to_kilometre_per_hour"]
}))
