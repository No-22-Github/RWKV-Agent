# DISTILL-CANARY-1a2e83a7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
edges = list(csv.DictReader(io.StringIO(files["pops/edge_peak_6173.tsv"]), delimiter="\t"))
peak = float(next(row["peak_megabits_per_second"] for row in edges if row["pop"] == "Manchester edge"))
units = {}
for row in csv.reader(io.StringIO(files["standards/throughput_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": peak * units["megabit_per_second_to_gigabyte_per_hour"]
}))
