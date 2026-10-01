# DISTILL-CANARY-a69f31b8 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/bakery_freight.csv"]))
total = Decimal("0")
for r in rows:
    if r["城市"] == "成都" and r["配送月份"] == "2026-09":
        total += Decimal(r["实付运费"])
print(json.dumps({"expected_number": float(total)}))
