# DISTILL-CANARY-ef74b0c2 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "lift/car-settings.csv"
text = case["files"][path]
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
drive = re.search(r"drive_type,([a-z]+)", text).group(1)
if drive != "gearless":
    raise SystemExit("the settings table must name the drive type fitted")
values = sorted(set(re.findall(r"speed (?:is set to|of) ([\d.]+) metres per second", pages)))
if len(values) != 2:
    raise SystemExit("the maker's notes do not give one trip speed per drive type")
filled = []
for line in text.split("\n"):
    if line.startswith("governor_trip_speed_m_per_s,"):
        line = "governor_trip_speed_m_per_s,1.6"
    filled.append(line)
print(json.dumps({"files": {path: "\n".join(filled).rstrip("\n")}}))
