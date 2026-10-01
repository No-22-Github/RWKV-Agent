# DISTILL-CANARY-f981ce10 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["inventory/bin-stock.tsv"]), delimiter="\t")
total = Decimal("0")
n = 0
for r in rows:
    if r["part_code"] == "FT-3306":
        total += Decimal(r["qty_on_hand"])
        n += 1
if n < 1:
    raise SystemExit("fixture guard failed: the target part rows are gone")
print(json.dumps({"expected_number": float(total)}))
