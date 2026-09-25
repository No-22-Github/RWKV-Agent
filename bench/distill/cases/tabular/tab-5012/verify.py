# DISTILL-CANARY-38ac74f9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
lines = list(csv.DictReader(io.StringIO(case["files"]["order_lines_2026-08.csv"])))
costs = {r["product_code"]: float(r["unit_cost"])
         for r in csv.DictReader(io.StringIO(case["files"]["product_costs.csv"]))}
total = 0.0
seen = set()
for line in lines:
    if line["line_id"] in seen:
        continue
    seen.add(line["line_id"])
    if line["warehouse"] == "Bellhaven":
        total += costs[line["product_code"]] * int(line["units"])
print(json.dumps({"expected_number": round(total, 2)}))
