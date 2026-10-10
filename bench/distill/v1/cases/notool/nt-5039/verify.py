# DISTILL-CANARY-44f2c737 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]


def clock_minutes(text):
    hours, minutes = text.strip().split(":")
    return int(hours) * 60 + int(minutes)


close = clock_minutes(
    next(row["close_time"] for row in
         csv.DictReader(io.StringIO(files["hubs/counter_times.csv"]))
         if row["hub"] == "Brisbane counter")
)
offsets = {}
for row in csv.DictReader(io.StringIO(files["standards/counter_offsets.csv"])):
    sign = -1 if row["offset_in_force"].startswith("-") else 1
    offsets[row["station"]] = sign * clock_minutes(row["offset_in_force"].lstrip("+-"))
print(json.dumps({"expected_number": close - offsets["Brisbane"]}))
