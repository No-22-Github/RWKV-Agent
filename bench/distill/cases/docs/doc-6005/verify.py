# DISTILL-CANARY-0607a128 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["releases/release-log.csv"]))

# README.md: one row per release, oldest first; the summary says what each
# release changed, so the first summary naming the feature is its arrival.
value = None
for row in rows:
    if "load balancing" in row["summary"].strip().lower():
        value = row["version"].strip()
        break

print(json.dumps({"expected_string": value}))
