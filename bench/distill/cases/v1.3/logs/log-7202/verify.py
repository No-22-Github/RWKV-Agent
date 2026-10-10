# DISTILL-CANARY-917b2e57 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/gateway-2026-09-03.log"].splitlines()

if not lines or not lines[0].startswith("# hollingworth-gw node"):
    raise SystemExit("fixture guard failed: journal header line is gone")
close = re.compile(r"^2026-09-03T23:59:47\.012Z CLOSE hollingworth-gw records=(\d+) status=clean$")
if not lines or not close.match(lines[-1]):
    raise SystemExit("fixture guard failed: journal close line is gone")
if int(close.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

rec = re.compile(r"^(2026-09-03T\d\d:\d\d:\d\d\.\d\d\dZ) (INFO|WARN|ERROR) (\S+) (.+)$")
lo, hi = "2026-09-03T14:05:00", "2026-09-03T14:20:00"
count = 0
for line in lines[1:-1]:
    m = rec.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, level, svc, msg = m.groups()
    if lo <= ts < hi and level == "ERROR" and svc == "hollingworth-pay-3ds":
        count += 1
print(json.dumps({"expected_number": count}))
