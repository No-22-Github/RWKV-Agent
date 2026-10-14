# DISTILL-CANARY-016c9d8c : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/extract_batches.tsv"]), delimiter="	")
total = Decimal("0")
for r in rows:
    if r["batch_month"] == "2026-09" and r["honey_type"] == "Wildflower":
        total += Decimal(r["wholesale_value"])
print(json.dumps({"expected_number": float(total)}))
