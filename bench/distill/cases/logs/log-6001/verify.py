# DISTILL-CANARY-b04a6f11 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/berth-loading.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

line_re = re.compile(
    r"^(\S+) BAY (\S+) tanker=(\S+) (LOAD START|PUMP ON|PUMP OFF|METER litres=\d+|LOAD COMPLETE litres=\d+)$")
bay_of = {}
loads = set()
for line in lines[:-1]:
    m = line_re.fullmatch(line)
    assert m, "unreadable line: " + line
    bay, tanker = m.group(2), m.group(3)
    assert bay_of.setdefault(tanker, bay) == bay, "tanker loaded at two bays"
    if "LOAD COMPLETE" in line:
        loads.add(tanker)
print(json.dumps({"expected_number": len(loads)}))
