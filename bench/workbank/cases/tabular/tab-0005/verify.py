# WORKBANK-CANARY-4b7d9e12 : bank artifact, excluded from training corpora
"""Recompute the Outbound department's February 2026 hours from the fixtures.

Reads the fixtures out of case.json (the same file the harness carries) and
joins the hours log to the roster on employee_id: a booked hour belongs to
the department the roster shows for that employee.
"""
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]

department_of = {}
for row in csv.DictReader(io.StringIO(files["employee_roster.csv"])):
    department_of[row["employee_id"]] = row["department"]

total = 0.0
for row in csv.DictReader(io.StringIO(files["hours_log_february_2026.csv"])):
    if department_of.get(row["employee_id"]) == "Outbound":
        total += float(row["hours"])

print(json.dumps({"expected_number": round(total, 2)}))
