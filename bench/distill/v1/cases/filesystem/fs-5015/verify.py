# DISTILL-CANARY-e5ab820a : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

booked, loaded = [], []
for line in case["files"]["wharf-sheet.txt"].splitlines():
    marks = [part.strip() for part in line.split(":", 1)[-1].split(",")]
    marks = [mark for mark in marks if mark]
    if line.startswith("Booked:"):
        booked = marks
    elif line.startswith("Loaded:"):
        loaded = marks

missing = [mark for mark in booked if mark not in loaded]
print(json.dumps({"expected_string": missing[0] if len(missing) == 1 else "UNKNOWN"}))
