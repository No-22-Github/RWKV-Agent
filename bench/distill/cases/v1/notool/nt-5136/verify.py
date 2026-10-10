# DISTILL-CANARY-331ac6f5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
stock = list(csv.DictReader(io.StringIO(files["warehouse/bottle_stock.tsv"]), delimiter="\t"))
held = float(next(row["held_gross"] for row in stock if row["item"] == "Amber 500ml"))
counts = {}
for row in csv.reader(io.StringIO(files["standards/pack_counts.csv"])):
    counts[row[0]] = float(row[1])
print(json.dumps({"expected_number": held * counts["gross_to_single"]}))
