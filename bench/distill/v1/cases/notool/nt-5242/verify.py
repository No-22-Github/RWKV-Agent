# DISTILL-CANARY-0d36501d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/yarn_count_units.csv"])):
    rates[row[0]] = float(row[1])
orders = list(csv.DictReader(io.StringIO(files["specs/yarn_order_6150.tsv"]), delimiter="\t"))
order = [row for row in orders if row["yarn"] == "BH-6150"][0]
print(json.dumps({
    "expected_number": float(order["count_tex"]) * rates["denier_per_tex"]
}))
