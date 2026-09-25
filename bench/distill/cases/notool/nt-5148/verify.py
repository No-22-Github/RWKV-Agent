# DISTILL-CANARY-8a02528d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
shifts = list(csv.DictReader(io.StringIO(files["berths/berth_shift_5093.tsv"]), delimiter="\t"))
row = next(item for item in shifts if item["berth"] == "3")
equivalents = {}
for item in csv.reader(io.StringIO(files["standards/box_equivalents.csv"])):
    equivalents[item[0]] = float(item[1])
print(json.dumps({
    "expected_number": float(row["forty_foot_boxes"]) * equivalents["forty_foot_box_to_teu"]
    + float(row["twenty_foot_boxes"]) * equivalents["twenty_foot_box_to_teu"]
}))
