# DISTILL-CANARY-04b91384 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/parcel_weights_2026-09.csv"])))
vals = [float(r["重量公斤"]) for r in rows if r["重量公斤"].strip() not in ("", "NA", "-")]
avg = sum(vals) / len(vals)
print(json.dumps({"expected_number": float(avg)}))
