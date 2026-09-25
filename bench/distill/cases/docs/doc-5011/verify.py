# DISTILL-CANARY-e18f72c3 : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]["revision-log.md"]

months = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]
month_number = {name: index for index, name in enumerate(months, 1)}
target = (2026, month_number["october"])

# The revision in force for a month is the one whose window has opened last.
in_force = None
for line in log.splitlines():
    match = re.match(r"Revision (\d+) applies to work carried out from (\w+) (\d{4})", line.strip())
    if not match:
        continue
    revision = int(match.group(1))
    starts = (int(match.group(3)), month_number[match.group(2).lower()])
    if starts <= target and (in_force is None or starts > in_force[0]):
        in_force = (starts, revision)

print(json.dumps({"expected_number": in_force[1]}))
