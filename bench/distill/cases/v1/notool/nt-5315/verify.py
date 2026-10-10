# DISTILL-CANARY-5d81e24c : distillation case
import csv
import io
import json

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["rates/storage-card-2026.csv"])))


def covers(spec, month):
    start, end = [part.strip() for part in spec.split(" to ")]
    index = MONTHS.index(month)
    first, last = MONTHS.index(start), MONTHS.index(end)
    if first <= last:
        return first <= index <= last
    return index >= first or index <= last


rate = next(float(r["per_pallet_week_gbp"]) for r in rows if covers(r["months"], "November"))
total = rate * 80 * 2
print(json.dumps({"expected_number": round(total, 2)}))
