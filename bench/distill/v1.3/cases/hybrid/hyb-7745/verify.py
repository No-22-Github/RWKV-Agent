# DISTILL-CANARY-e7c20d58 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/bookings_october.csv"])))
no_shows = sum(1 for r in rows if r["no_show"] == "yes")
fees = sum(float(r["late_fee_usd"]) for r in rows)
print(json.dumps({
    "expected_number": no_shows,
    "turn_2_expected_number": round(fees, 2),
}))
