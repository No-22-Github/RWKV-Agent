# WORKBANK-CANARY-6b0f8d34 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
units = {
    r["sku"]: float(r["units"])
    for r in csv.DictReader(io.StringIO(files["stock_scan.tsv"]), delimiter="\t")
}
point = {
    r["sku"]: float(r["reorder_point"])
    for r in csv.DictReader(io.StringIO(files["reorder_plan.csv"]))
}
cost = {
    r["sku"]: float(r["unit_cost"])
    for r in csv.DictReader(io.StringIO(files["unit_costs.csv"]))
}
total = 0.0
for sku, held in units.items():
    if held < point[sku]:
        total += held * cost[sku]
print(json.dumps({"expected_number": round(total, 2)}))
