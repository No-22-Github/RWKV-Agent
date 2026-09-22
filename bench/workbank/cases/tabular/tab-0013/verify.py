# WORKBANK-CANARY-4f1a9c2d : bank artifact, excluded from training corpora
import csv
import io
import json
import re

case = json.load(open("case.json"))

rates = {}
for line in case["files"]["rates.md"].splitlines():
    m = re.match(r"\|\s*([A-Z])\s*\|.*\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*$", line)
    if m:
        rates[m.group(1)] = float(m.group(2))

rows = list(csv.reader(io.StringIO(case["files"]["consignments_october_2025.csv"])))
total = 0.0
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    total += rates[row[3].strip()]

print(json.dumps({"expected_number": round(total, 2)}))
