# DISTILL-CANARY-b04ad460 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/still-house.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ INFO still=\S+ .+$")
warn_re = re.compile(r"^\S+ WARN still=\S+ .+$")
err_re = re.compile(r"^\S+ ERROR still=\S+ code=(\S+) msg=")
codes = []
for line in lines[:-1]:
    m = err_re.match(line)
    if m:
        codes.append(m.group(1))
    else:
        assert info_re.fullmatch(line) or warn_re.fullmatch(line), "unreadable line: " + line
assert len(codes) == 1, "the journal should carry exactly one ERROR"
print(json.dumps({"expected": codes[0]}))
