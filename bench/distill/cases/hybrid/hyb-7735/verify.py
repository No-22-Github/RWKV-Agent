# DISTILL-CANARY-2e95b6d0 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/april_dispatches.csv"]))

def in_first_week(raw):
    if "-" in raw:
        year, month, day = raw.split("-")
    else:
        month, day, year = raw.split("/")
    return int(year) == 2026 and int(month) == 4 and int(day) <= 7

first_week = [r for r in rows if in_first_week(r["date"])]
units = sum(int(r["units"]) for r in first_week)
northgate = sum(int(r["units"]) for r in first_week if r["destination"] == "Northgate")
print(json.dumps({
    "expected_number": units,
    "turn_2_expected_number": northgate,
}))
