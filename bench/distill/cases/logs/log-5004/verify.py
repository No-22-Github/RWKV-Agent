# DISTILL-CANARY-edddbdaf : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/flowmeter.log"].splitlines() if line.strip()]
header = re.fullmatch(r"session=(\d{4}-\d{2}-\d{2}) instrument=\S+ site=\S+", lines[0])
assert header is not None, "session header missing"
assert header.group(1) == "2026-08-03", "unexpected session date"

start, end = "14:10:00", "14:45:00"
flagged = 0
for line in lines[1:]:
    match = re.fullmatch(r"(\d{2}:\d{2}:\d{2}) (INFO|ALARM) reading=\d+\.\d+", line)
    assert match is not None, "unreadable reading line: " + line
    stamp, level = match.group(1), match.group(2)
    if level == "ALARM" and start <= stamp < end:
        flagged += 1
print(json.dumps({"expected_number": flagged}))
