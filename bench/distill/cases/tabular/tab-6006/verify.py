# DISTILL-CANARY-6c266545 : distillation case
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
rows = list(csv.DictReader(io.StringIO(case["files"]["jobs_april_2026.csv"])))
total = sum(float(r["hours"]) for r in rows
            if date(2026, 4, 1) <= as_day(r["completed_date"]) <= date(2026, 4, 7))
print(json.dumps({"expected_number": round(total, 2)}))
