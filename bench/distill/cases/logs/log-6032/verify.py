# DISTILL-CANARY-b04b5d19 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/bottling-line.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

line_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) LINE L1 (start batch=\S+ bottles_planned=\d+|stop batch=\S+ bottles_done=\d+|pallet sealed crates=\d+)$")
count = 0
for line in lines[:-1]:
    m = line_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if "pallet sealed" in m.group(3) and m.group(1) == "2026-07-09" and "10:00:00" <= m.group(2) < "11:00:00":
        count += 1
print(json.dumps({"expected_number": count}))
