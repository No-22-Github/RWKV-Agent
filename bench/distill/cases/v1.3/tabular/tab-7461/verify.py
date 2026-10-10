# DISTILL-CANARY-88b5d1d6 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/bookings_2026-07.csv"])))
n = sum(1 for r in rows if r["来源"] == "老客推荐")
print(json.dumps({"expected_number": float(n)}))
