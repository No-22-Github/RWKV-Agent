# DISTILL-CANARY-b2622068 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
awards = list(csv.DictReader(io.StringIO(case["files"]["awards/awards.csv"])))
payments = list(csv.DictReader(io.StringIO(case["files"]["awards/payments.csv"])))
valid = {a["award_id"] for a in awards}
seen = set()
total = 0.0
for p in payments:
    key = (p["payment_id"], p["award_ref"], p["paid_on"], p["amount"])
    if key in seen or p["award_ref"] not in valid:
        continue
    seen.add(key)
    total += float(p["amount"])
print(json.dumps({"expected_number": round(total, 2)}))
