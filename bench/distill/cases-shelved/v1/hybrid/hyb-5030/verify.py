# DISTILL-CANARY-16b8d4a7 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["consignments/september-2026.csv"])))
if not rows:
    raise SystemExit("the consignment file is empty")
types = {row["crate_type"] for row in rows}
if types != {"standard"}:
    raise SystemExit("the consignments must all be packed in one crate type")
page = next(entry["content"] for entry in case["web_fixture"] if "standard crate weighs" in entry["content"])
tare = float(re.search(r"standard crate weighs ([\d.]+) kg", page).group(1))
export = float(re.search(r"export crate weighs ([\d.]+) kg", page).group(1))
if tare == export:
    raise SystemExit("the two crate types must not weigh the same")
net = sum(float(row["gross_kg"]) - int(row["crates"]) * tare for row in rows)
assert net > 0, "the fruit must weigh something"
print(json.dumps({"expected_number": round(net, 2)}))
