# DISTILL-CANARY-b04f6d84 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/turbine-events.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

start_re = re.compile(r"^\S+ turbine=(\S+) yaw_start wind_from_deg=\d+$")
stop_re = re.compile(r"^\S+ turbine=\S+ yaw_stop wind_from_deg=\d+$")
other_re = re.compile(r"^\S+ turbine=\S+ (fault_reset|derate)$")
starts = 0
for line in lines[:-1]:
    m = start_re.fullmatch(line)
    if m:
        if m.group(1) == "T-2":
            starts += 1
    else:
        assert stop_re.fullmatch(line) or other_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": starts}))
