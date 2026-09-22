# WORKBANK-CANARY-c2a94e71 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
cost = {
    r["sku"]: float(r["unit_cost"])
    for r in csv.DictReader(io.StringIO(files["standard_costs.csv"]))
}
lines = files["stocktake_2026-09-14.csv"].split("\n")
start = next(i for i, line in enumerate(lines) if line.startswith("sku,"))
total = 0.0
for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
    units = float(row["units"])
    if row["sku"] == "Grand total" or units < 20:
        continue
    total += units * cost[row["sku"]]
print(json.dumps({"expected_number": round(total, 2)}))
