# DISTILL-CANARY-b04e4108 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/pump-house.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ INFO pump=\S+ \S+ ok$")
note_re = re.compile(r"^\S+ NOTE .+$")
fault_re = re.compile(r"^(\S+) FAULT pump=(\S+) code=\S+ msg=")
first = None
for line in lines[:-1]:
    m = fault_re.match(line)
    if m:
        if first is None:
            first = m.group(2)
    elif note_re.fullmatch(line) or info_re.fullmatch(line):
        pass
    else:
        raise AssertionError("unreadable line: " + line)
assert first is not None, "no FAULT line in the journal"
print(json.dumps({"expected": first}))
