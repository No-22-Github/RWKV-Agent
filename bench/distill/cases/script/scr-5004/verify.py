# DISTILL-CANARY-7c3b51ea : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

totals = {}
for path in ["nights/2026-08.csv", "nights/2026-09.csv"]:
    for row in csv.DictReader(io.StringIO(files[path])):
        totals[row["observer"]] = totals.get(row["observer"], 0) + int(row["minutes"])
for row in csv.DictReader(io.StringIO(hidden["nights/2026-10.csv"])):
    totals[row["observer"]] = totals.get(row["observer"], 0) + int(row["minutes"])

print(json.dumps({
    "expected_stdout": "TOTAL,%d" % sum(totals.values()),
    "files": {"nights/2026-08.csv": files["nights/2026-08.csv"]},
}))
