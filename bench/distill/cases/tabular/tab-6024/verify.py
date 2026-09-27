# DISTILL-CANARY-90304c33 : distillation case
import csv
import io
import json
from datetime import date

MONTHS = {}
for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
    MONTHS[m] = i + 1


def as_day(text):
    text = text.strip()
    if "/" in text:
        d, m, y = text.split("/")
        return date(int(y), int(m), int(d))
    if "-" in text:
        y, m, d = text.split("-")
        return date(int(y), int(m), int(d))
    parts = text.split()
    return date(int(parts[2]), MONTHS[parts[1]], int(parts[0]))


case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["bookings/coach_bookings_q2_2026.csv"])))
per = {}
for r in rows:
    d = as_day(r["service_date"])
    per[d.month] = per.get(d.month, 0) + int(r["passengers"])
print(json.dumps({"expected_number": max(per.values())}))
