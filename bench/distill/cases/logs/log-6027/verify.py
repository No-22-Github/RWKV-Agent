# DISTILL-CANARY-b04c7d65 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/oven-log.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

slot_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) SLOT s=\d+ (load|unload) loaves=\d+$")
count = 0
for line in lines[:-1]:
    m = slot_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if m.group(1) == "2026-05-21" and "06:00:00" <= m.group(2) < "08:00:00" and m.group(3) == "load":
        count += 1
print(json.dumps({"expected_number": count}))
