# WORKBANK-CANARY-c60b3fa7 : bank artifact, excluded from training corpora
"""Recompute August pay for the Moulding department from the fixtures.

The hours sheet opens with a three-line report block, so the table starts at
the line whose first field is employee_id; its closing TOTAL line carries no
roster id and is the whole sheet's figure. Rates, department and shift come
from crew_list.csv. Pay per person: 176 hours at the hourly rate, hours past
176 at 1.5x, and for the night shift every hour at 1.25x with no step.
"""
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]

THRESHOLD = 176.0
OVERTIME = 1.5
NIGHT = 1.25

crew = {}
for row in csv.DictReader(io.StringIO(files["crew_list.csv"])):
    crew[row["employee_id"]] = row

lines = files["shift_hours_august_2026.csv"].splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith("employee_id"))

recorded = {}
for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
    if row["employee_id"].strip().upper() == "TOTAL":
        continue
    recorded[row["employee_id"]] = float(row["hours"])

total = 0.0
for employee_id, hours in recorded.items():
    person = crew.get(employee_id)
    if person is None or person["department"] != "Moulding":
        continue
    rate = float(person["hourly_rate"])
    if person["shift"] == "night":
        total += rate * NIGHT * hours
    else:
        straight = min(hours, THRESHOLD)
        extra = max(hours - THRESHOLD, 0.0)
        total += rate * (straight + OVERTIME * extra)

print(json.dumps({"expected_number": round(total, 2)}))
