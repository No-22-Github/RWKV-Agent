# DISTILL-CANARY-ee948f14 : distillation case
import csv
import io
import json
from decimal import Decimal
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/resale_2026-09.csv"]))
net = defaultdict(Decimal)
for r in rows:
    if r["sale_month"] == "2026-09":
        net[r["vendor"]] += Decimal(r["sale_gbp"]) - Decimal(r["return_gbp"])
print(json.dumps({"expected_number": float(max(net.values()))}))
