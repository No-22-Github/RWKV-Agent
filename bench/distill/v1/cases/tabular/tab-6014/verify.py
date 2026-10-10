# DISTILL-CANARY-1765a97d : distillation case
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
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/orders_june_2026.csv"])))
count = sum(1 for r in rows
            if date(2026, 6, 8) <= as_day(r["placed_on"]) <= date(2026, 6, 14))
print(json.dumps({"expected_number": count}))
