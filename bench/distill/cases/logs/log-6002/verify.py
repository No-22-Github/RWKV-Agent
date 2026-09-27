# DISTILL-CANARY-b04b2d70 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/irrigation.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

open_re = re.compile(r"^\S+ bed=(\S+) valve=(\S+) OPEN minutes=\d+$")
opens = 0
for line in lines[:-1]:
    m = open_re.fullmatch(line)
    if m:
        if m.group(1) == "fernery":
            opens += 1
    else:
        assert re.fullmatch(r"\S+ bed=\S+ valve=\S+ CLOSE", line), "unreadable line: " + line
print(json.dumps({"expected_number": opens}))
