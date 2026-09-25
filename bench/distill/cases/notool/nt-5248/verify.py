# DISTILL-CANARY-0cf8810e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
units = {}
for row in csv.reader(io.StringIO(files["standards/paper_units.csv"])):
    units[row[0]] = float(row[1])
holds = list(csv.DictReader(io.StringIO(files["stock/paper_hold_1806.tsv"]), delimiter="\t"))
hold = [row for row in holds if row["stock"] == "PF-1806"][0]
print(json.dumps({
    "expected_number": float(hold["reams"]) * units["sheet_per_ream"]
}))
