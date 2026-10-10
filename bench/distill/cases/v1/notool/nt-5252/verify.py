# DISTILL-CANARY-f2ff7b62 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
offsets = {}
for row in csv.reader(io.StringIO(files["standards/site_offsets.csv"])):
    offsets[row[0]] = float(row[1])
loaded = list(csv.DictReader(io.StringIO(files["timetables/departure_4417.tsv"]), delimiter="\t"))
slot = [row for row in loaded if row["service"] == "RT-4417"][0]
key = slot["origin"].replace(" ", "_") + "_minutes_ahead_of_utc"
hours, minutes = slot["clock_time"].split(":")
local_minutes = int(hours) * 60 + int(minutes)
print(json.dumps({
    "expected_number": (local_minutes - offsets[key]) * 60
}))
