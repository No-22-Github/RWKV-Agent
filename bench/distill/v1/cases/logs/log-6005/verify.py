# DISTILL-CANARY-b04e7726 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/lock3-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

in_re = re.compile(r"^\S+ VESSEL IN boat=(\S+)$")
out_re = re.compile(r"^\S+ VESSEL OUT boat=(\S+)$")
lock_re = re.compile(r"^\S+ LOCK 3 (OPEN|CLOSED)$")
note_re = re.compile(r"^\S+ NOTE .+$")
entered, left = set(), set()
for line in lines[:-1]:
    m = in_re.fullmatch(line)
    n = out_re.fullmatch(line)
    if m:
        assert m.group(1) not in entered, "boat entered twice"
        entered.add(m.group(1))
    elif n:
        left.add(n.group(1))
    elif lock_re.fullmatch(line):
        pass
    else:
        assert note_re.fullmatch(line), "unreadable line: " + line
assert left <= entered, "a boat left that never entered"
print(json.dumps({"expected_number": len(entered & left)}))
