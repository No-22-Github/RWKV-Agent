# WORKBANK-CANARY-8d3e6b05 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
on_hand = {
    r["sku"]: float(r["units"])
    for r in csv.DictReader(io.StringIO(files["stock_scan.tsv"]), delimiter="\t")
}
point = {
    r["sku"]: float(r["reorder_point"])
    for r in csv.DictReader(io.StringIO(files["replenishment_plan.csv"]))
}
below = [sku for sku in on_hand if on_hand[sku] < point[sku]]
print(json.dumps({"expected_number": len(below)}))
