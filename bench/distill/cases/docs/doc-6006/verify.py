# DISTILL-CANARY-fad5e141 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["releases/release-log.csv"])))

# README.md: a capability that no summary mentions has never shipped in a
# drive release.
value = "UNKNOWN"
for row in rows:
    if "snmpv3" in row["summary"].strip().lower():
        value = row["version"].strip()
        break

print(json.dumps({"expected_string": value}))
