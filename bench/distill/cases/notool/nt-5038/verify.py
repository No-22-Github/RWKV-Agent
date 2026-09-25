# DISTILL-CANARY-90e66db3 : distillation case
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
         csv.DictReader(io.StringIO(files["depots/gate_times.csv"]))
         if row["depot"] == "Kathmandu gates")
)
offsets = {}
for row in csv.DictReader(io.StringIO(files["standards/station_offsets.csv"])):
    sign = -1 if row["offset_in_force"].startswith("-") else 1
    offsets[row["station"]] = sign * clock_minutes(row["offset_in_force"].lstrip("+-"))
print(json.dumps({"expected_number": close - offsets["Kathmandu"]}))
