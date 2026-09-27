# DISTILL-CANARY-b04b7e28 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/gate-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ INFO gate controller firmware cut over to version [\d.]+$")
pass_re = re.compile(r"^\S+ INFO gate=linkspan-\d+ vehicle=car pass=granted lane=\d+$")
err_re = re.compile(r"^(\S+) ERROR gate=linkspan-\d+ code=(\S+) msg=")
warn_re = re.compile(r"^\S+ WARN gate=linkspan-\d+ code=\S+ msg=\"[^\"]+\"$")
cutover = None
first = None
for line in lines[:-1]:
    m = err_re.fullmatch(line + " ")
    m = err_re.match(line)
    if m:
        if cutover is not None and first is None:
            first = m.group(2)
    elif info_re.fullmatch(line):
        assert cutover is None, "two cutover markers"
        cutover = line.split("T")[1].split(" ")[0]
    elif pass_re.fullmatch(line) or warn_re.fullmatch(line):
        pass
    else:
        raise AssertionError("unreadable line: " + line)
assert cutover is not None and first is not None, "cutover marker or post-cutover error absent"
print(json.dumps({"expected": first}))
