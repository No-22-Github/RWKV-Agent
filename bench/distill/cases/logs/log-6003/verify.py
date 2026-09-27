# DISTILL-CANARY-b04c5e93 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/crac-alarms.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

line_re = re.compile(
    r"^\S+ host=(\S+) (INFO|WARN|ERROR)(?: code=(\S+))? (?:return_air_c=[\d.]+ setpoint_c=[\d.]+|fan_rpm=\d+ setpoint_c=[\d.]+)$")
errors = 0
for line in lines[:-1]:
    m = line_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if m.group(2) == "ERROR" and m.group(1) == "kilmorie-crac-2":
        errors += 1
print(json.dumps({"expected_number": errors}))
