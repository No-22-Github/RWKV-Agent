# DISTILL-CANARY-d40517b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]


def clock_minutes(text):
    hours, minutes = text.strip().split(":")
    return int(hours) * 60 + int(minutes)


offsets = {}
for row in csv.DictReader(io.StringIO(files["standards/desk_offsets.csv"])):
    sign = -1 if row["offset_in_force"].startswith("-") else 1
    offsets[row["station"]] = sign * clock_minutes(row["offset_in_force"].lstrip("+-"))
desks = {
    row["station"]: row["desk"]
    for row in csv.DictReader(io.StringIO(files["desks/duty_desks.csv"]))
}
assert desks["Phoenix"] == "Phoenix desk"
assert desks["Lagos"] == "Lagos desk"
print(json.dumps({"expected_number": offsets["Lagos"] - offsets["Phoenix"]}))
