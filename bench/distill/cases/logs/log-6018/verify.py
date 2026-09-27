# DISTILL-CANARY-b04f2279 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/sawmill-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ host=\S+ INFO boards_m=\d+ feed_m_min=\d+$")
err_re = re.compile(r"^(\S+) host=(\S+) ERROR code=(\S+) msg=")
warn_re = re.compile(r"^\S+ host=\S+ WARN code=\S+ msg=\"[^\"]+\"$")
first = None
for line in lines[:-1]:
    m = err_re.fullmatch(line + " ")
    m = err_re.match(line)
    if m:
        if m.group(2) == "minnigaff-sawline-2" and first is None:
            first = m.group(3)
    elif warn_re.fullmatch(line) or info_re.fullmatch(line):
        pass
    else:
        raise AssertionError("unreadable line: " + line)
assert first is not None, "no sawline-2 error in the journal"
print(json.dumps({"expected": first}))
