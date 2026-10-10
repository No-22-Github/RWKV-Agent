# DISTILL-CANARY-f3d91b60 : distillation case
import json
import re

case = json.load(open("case.json"))
schedule = case["files"]["fees/test-fees.md"]
conditions = case["files"]["conditions.txt"]

# The schedule is a markdown table: service | turnaround | fee.
fees = {}
for line in schedule.splitlines():
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) == 3 and re.fullmatch(r"\d+(?:\.\d+)?", cells[2]):
        fees[cells[0]] = float(cells[2])

# The conditions put a surcharge on a test started within two working days.
percent = 0
match = re.search(r"surcharge: (\d+) per cent", conditions)
if match:
    percent = int(match.group(1))

print(json.dumps({"expected_number": round(fees["Chemical screen"] * (1 + percent / 100), 2)}))
