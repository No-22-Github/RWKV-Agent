# DISTILL-CANARY-1b6040e7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]


def clock_seconds(text):
    hours, minutes = text.strip().split(":")
    return (int(hours) * 60 + int(minutes)) * 60


slots = list(csv.DictReader(io.StringIO(files["timetables/path_slots.tsv"]), delimiter="\t"))
booked = next(row["booked"] for row in slots if row["station"] == "Chatham Islands")
offsets = {}
for row in csv.reader(io.StringIO(files["standards/station_offsets.csv"])):
    sign = -1 if row[1].startswith("-") else 1
    offsets[row[0]] = sign * clock_seconds(row[1].lstrip("+-"))
print(json.dumps({"expected_number": clock_seconds(booked) - offsets["Chatham Islands"]}))
