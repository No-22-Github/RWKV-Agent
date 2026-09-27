# DISTILL-CANARY-b04c04a1 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/pump-station.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ INFO pump=\S+ .+$")
err_re = re.compile(r"^\S+ ERROR pump=(\S+) suction_bar=([\d.]+) msg=")
vals = []
for line in lines[:-1]:
    m = err_re.match(line)
    if m:
        assert m.group(1) == "P-2", "error on an unexpected pump"
        vals.append(float(m.group(2)))
    else:
        assert info_re.fullmatch(line), "unreadable line: " + line
assert len(vals) == 1, "the journal should carry exactly one ERROR"
print(json.dumps({"expected_number": vals[0]}))
