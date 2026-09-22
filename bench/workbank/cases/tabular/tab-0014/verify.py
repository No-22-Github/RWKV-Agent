# WORKBANK-CANARY-9b3e7d15 : bank artifact, excluded from training corpora
import csv
import io
import json
import math
import re

case = json.load(open("case.json"))


def tariff_bands(text):
    bands = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 2:
            continue
        try:
            bands[cells[0]] = float(cells[1])
        except ValueError:
            continue
    return bands


bands = tariff_bands(case["files"]["tariff-card.md"])
light = bands["up to 20 kg"]
mid = bands["over 20 kg up to 40 kg"]

cond = case["files"]["lane-conditions.md"]
first40 = float(re.search(r"([0-9]+(?:\.[0-9]+)?) for the first 40 kg", cond).group(1))
step = float(re.search(r"([0-9]+(?:\.[0-9]+)?) for each further 5 kg", cond).group(1))

rows = list(csv.reader(io.StringIO(case["files"]["manifest_march_2026.csv"])))
total = 0.0
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    weight = float(row[2])
    if weight > 40:
        total += first40 + step * math.ceil((weight - 40) / 5)
    elif weight > 20:
        total += mid
    else:
        total += light

print(json.dumps({"expected_number": round(total, 2)}))
