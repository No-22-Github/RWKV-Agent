# DISTILL-CANARY-b04d18f4 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/dryer-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

line_re = re.compile(r"^\S+ drier=(\S+) batch=\S+ (START moisture_in=[\d.]+|DONE hours=[\d.]+)$")
done = 0
for line in lines[:-1]:
    m = line_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if "DONE" in line and m.group(1) == "D-2":
        done += 1
print(json.dumps({"expected_number": done}))
