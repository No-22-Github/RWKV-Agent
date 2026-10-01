# DISTILL-CANARY-658cc644 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["promo/bundle_2026-10.csv"])))
price = next(float(r["定价元"]) for r in rows if r["书目"].startswith("城市植物志"))
discounted = price * 0.9
value = discounted - 50 if discounted >= 400 else discounted
print(json.dumps({"expected_number": value}))
