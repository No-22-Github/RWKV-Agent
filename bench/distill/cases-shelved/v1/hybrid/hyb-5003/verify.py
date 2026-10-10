# DISTILL-CANARY-91be44c0 : distillation case
import csv
import io
import json
import math
import re

LENGTH_METRES = 8.5


def band_bounds(label):
    numbers = [int(value) for value in re.findall(r"\d+", label)]
    if "or less" in label:
        return 0, numbers[0]
    if "or more" in label:
        return numbers[0], 10 ** 6
    return numbers[0], numbers[1]


case = json.load(open("case.json"))
charged_metres = math.ceil(LENGTH_METRES)
rate = None
rows = csv.DictReader(io.StringIO(case["files"]["yard/storage-charges-2026.csv"]))
for row in rows:
    low, high = band_bounds(row["length_band"])
    if low <= charged_metres <= high:
        rate = float(row["charge_per_metre"])
        break
if rate is None:
    raise SystemExit("no band covers the charged length")
print(json.dumps({"expected_number": round(charged_metres * rate, 2)}))
