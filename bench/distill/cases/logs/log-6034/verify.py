# DISTILL-CANARY-b04d7a53 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/dock-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

dep_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) DEPART door=\S+ trailer=\S+ turnaround=(\S*)$")
count = 0
for line in lines[:-1]:
    m = dep_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if m.group(1) == "2026-09-15" and "08:00:00" <= m.group(2) < "09:00:00":
        if re.fullmatch(r"\d{2}:\d{2}:\d{2}", m.group(3)):
            count += 1
print(json.dumps({"expected_number": count}))
