# DISTILL-CANARY-41cb1f03 : distillation case
import csv
import io
import json
from decimal import Decimal
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/lane_fees_2026-09.csv"]))
tot = defaultdict(Decimal)
for r in rows:
    if r["receipt_month"] == "2026-09":
        tot[r["league_night"]] += Decimal(r["fee_gbp"])
print(json.dumps({"expected_number": float(max(tot.values()))}))
