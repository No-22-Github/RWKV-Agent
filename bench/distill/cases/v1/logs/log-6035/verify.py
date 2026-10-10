# DISTILL-CANARY-b04e1fa8 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/water-quality.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

read_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2}) BED (\S+) salinity=[\d.]+ temp_c=[\d.]+ flag=(\S+)$")
note_re = re.compile(r"^\S+ NOTE .+$")

def night_of(date, hour):
    # a night runs from 18:00 to the following 06:00 (README)
    d = int(date[-2:])
    if hour >= 18:
        return d
    return d - 1

flags = 0
for line in lines[:-1]:
    m = read_re.fullmatch(line)
    if m:
        if night_of(m.group(1), int(m.group(2))) == 20 and m.group(6) == "low-salinity":
            flags += 1
    else:
        assert note_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": flags}))
