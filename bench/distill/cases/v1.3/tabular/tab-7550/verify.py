# DISTILL-CANARY-4f0dfe24 : distillation case
import csv
import io
import json
from decimal import Decimal
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/landings_2026-09.csv"]))
tot = defaultdict(Decimal)
for r in rows:
    if r["landing_date"] in ("2026-09-05", "05/09/2026"):
        tot[r["operator"]] += Decimal(r["value_gbp"])
print(json.dumps({"expected_number": float(max(tot.values()))}))
