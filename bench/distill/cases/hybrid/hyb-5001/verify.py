# DISTILL-CANARY-c1131e67 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "ravensbourne-freight.example" in e["url"])
rates = {}
for line in page["content"].splitlines():
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) == 2 and cells[0].startswith("Zone "):
        rates[cells[0]] = float(cells[1])
rows = csv.DictReader(io.StringIO(case["files"]["depot/despatch-log-2026-09.csv"]))
total = 0.0
for row in rows:
    total += float(row["chargeable_kg"]) * rates[row["destination_zone"]]
print(json.dumps({"expected_number": round(total, 2)}))
