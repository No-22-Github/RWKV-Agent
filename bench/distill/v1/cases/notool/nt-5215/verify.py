# DISTILL-CANARY-0d84bf19 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["pricing/label-bands-2026-09.csv"])))
band = next(r for r in rows if float(r["from_labels"]) <= 14000 <= float(r["to_labels"]))
total = float(band["price_per_thousand_gbp"]) * 14
print(json.dumps({"expected_number": round(total, 2)}))
