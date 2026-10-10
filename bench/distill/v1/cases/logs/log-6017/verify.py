# DISTILL-CANARY-b04e89b6 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/kiln-log.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ INFO zone=\S+ .+$")
fault_re = re.compile(r"^\S+ FAULT zone=\S+ code=(\S+) msg=")
codes = []
for line in lines[:-1]:
    m = fault_re.match(line)
    if m:
        codes.append(m.group(1))
    else:
        assert info_re.fullmatch(line), "unreadable line: " + line
assert len(codes) == 1, "the journal should carry exactly one FAULT"
print(json.dumps({"expected": codes[0]}))
