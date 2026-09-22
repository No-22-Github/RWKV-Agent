# WORKBANK-CANARY-a93c2f60 : bank artifact, excluded from training corpora
"""Recompute the Grounds department's April 2026 hours from the fixtures.

The hours sheet opens with three report lines, so the table starts at the
line whose first field is employee_id; the sheet closes with a TOTAL line,
which is the whole sheet's figure and is not a person's hours. A booked
hour belongs to the department the roster shows for that employee.
"""
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]

department_of = {}
for row in csv.DictReader(io.StringIO(files["employee_roster.csv"])):
    department_of[row["employee_id"]] = row["department"]

lines = files["hours_april_2026.csv"].splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith("employee_id"))

total = 0.0
for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
    if row["employee_id"].strip().upper() == "TOTAL":
        continue
    if department_of.get(row["employee_id"]) == "Grounds":
        total += float(row["hours"])

print(json.dumps({"expected_number": round(total, 2)}))
