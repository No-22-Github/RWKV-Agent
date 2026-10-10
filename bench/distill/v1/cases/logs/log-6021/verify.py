# DISTILL-CANARY-b04c6a42 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/pickling-line.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

iso_re = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2} (INFO .+|ERROR unit=\S+ code=\S+ msg=.+)$")
dmy_re = re.compile(r"^(\d{2})/(\d{2})/(\d{4}) \d{2}:\d{2}:\d{2} (INFO .+|ERROR unit=(\S+) code=\S+ msg=.+)$")
note_re = re.compile(r"^\S+ NOTE journal rotated: stamps switch to dd/mm/yyyy$")
units = []
for line in lines[:-1]:
    m = dmy_re.fullmatch(line)
    if m:
        if m.group(1) == "01" and m.group(2) == "02" and m.group(5):
            units.append(m.group(5))
        continue
    if iso_re.fullmatch(line) or note_re.fullmatch(line):
        continue
    raise AssertionError("unreadable line: " + line)
assert len(units) == 1, "1 February should carry exactly one ERROR"
print(json.dumps({"expected": units[0]}))
