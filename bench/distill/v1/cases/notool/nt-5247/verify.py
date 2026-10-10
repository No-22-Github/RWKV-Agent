# DISTILL-CANARY-9ef6cb00 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
densities = {}
for row in csv.reader(io.StringIO(files["standards/bulk_densities.csv"])):
    densities[row[0]] = float(row[1])
note = json.loads(files["transfers/waste_note_3720.json"])
print(json.dumps({
    "expected_number": note["mass_tonnes"] / densities["washed_sand_tonne_per_cubic_metre"]
}))
