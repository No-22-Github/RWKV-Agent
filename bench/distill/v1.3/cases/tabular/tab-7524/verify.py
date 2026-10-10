# DISTILL-CANARY-404c16f4 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/shipments.tsv"]), delimiter="	")
total = Decimal("0")
for r in rows:
    if r["发货月份"] == "2026-09" and r["渠道"] == "花市代发":
        total += Decimal(r["货款"])
print(json.dumps({"expected_number": float(total)}))
