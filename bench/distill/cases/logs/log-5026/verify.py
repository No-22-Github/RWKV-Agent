# DISTILL-CANARY-6b8f12e5 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/curtailment.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE lines=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every instruction"

hits = 0
for line in lines[:-1]:
    m = re.fullmatch(r"(\d{4}-\d\d-\d\d)T(\d\d):\d\d:\d\dZ (\S+) (\S+) setpoint_kw=\d+", line)
    assert m is not None, "unreadable instruction line: " + line
    if m.group(1) == "2026-09-23" and m.group(3) == "T-7" and m.group(4) == "CURTAIL" \
            and 12 <= int(m.group(2)) < 18:
        hits += 1
print(json.dumps({"expected_number": hits}))
