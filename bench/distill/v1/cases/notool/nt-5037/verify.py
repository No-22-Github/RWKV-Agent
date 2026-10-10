# DISTILL-CANARY-69abc080 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["casks/cask_runs_2026-08.csv"])))
casks = sum(float(row["count"]) for row in rows)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/cask_conversions.csv"]))
}
print(json.dumps({
    "expected_number": casks * table["kilderkin to imperial gallon"]
}))
