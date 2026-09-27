# DISTILL-CANARY-b04b194a : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/intake-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

open_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):\d{2} GATE (\S+) OPEN$")
close_re = re.compile(r"^\S+ GATE \S+ CLOSE$")
level_re = re.compile(r"^\S+ LEVEL head_m=[\d.]+ tail_m=[\d.]+$")
opened = 0
for line in lines[:-1]:
    m = open_re.fullmatch(line)
    if m:
        # 20:00-21:00 UTC is 22:00-23:00 on the plant clock, two hours ahead
        if m.group(1) == "2025-10-12" and "22:00" <= f"{m.group(2)}:{m.group(3)}" < "23:00":
            opened += 1
    else:
        assert close_re.fullmatch(line) or level_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": opened}))
