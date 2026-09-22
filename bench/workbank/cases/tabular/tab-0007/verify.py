# WORKBANK-CANARY-7e15c8d4 : bank artifact, excluded from training corpora
"""Recompute the Picking department's average hours per worker (June 2026).

The README sets the denominator: the average runs over the workers of the
department who have an hours figure for the month. In pick_log_june_2026.csv
an hours figure may be written as an empty cell, NA or "-"; those are not
figures, so such a worker is left out of both the total and the count.
"""
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]

department_of = {}
for row in csv.DictReader(io.StringIO(files["employee_roster.csv"])):
    department_of[row["employee_id"]] = row["department"]


def figure(cell):
    text = cell.strip()
    if text in ("", "NA", "-"):
        return None
    return float(text)


total = 0.0
count = 0
for row in csv.DictReader(io.StringIO(files["pick_log_june_2026.csv"])):
    if department_of.get(row["employee_id"]) != "Picking":
        continue
    hours = figure(row["hours"])
    if hours is None:
        continue
    total += hours
    count += 1

print(json.dumps({"expected_number": round(total / count, 3)}))
