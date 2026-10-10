# DISTILL-CANARY-5ec3d8ad : distillation case
import json
import re
from datetime import datetime

case = json.load(open("case.json"))
lines = case["files"]["logs/coldstore-2026-07-30.log"].splitlines()

if not lines or not lines[0].startswith("# wroxhall coldstore telemetry"):
    raise SystemExit("fixture guard failed: journal header line is gone")
close = re.match(r"^(2026-07-30T\d\d:\d\d:\d\d\.\d\d\dZ) CLOSE portal-utc records=(\d+) status=nominal$", lines[-1] if lines else "")
if close is None:
    raise SystemExit("fixture guard failed: journal close line is gone")
if int(close.group(2)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

rec = re.compile(r"^(\S+) (INFO|WARN|ALARM|CLOSE) (\S+) (.+)$")

def utc_clock(stamp):
    if stamp.endswith("Z"):
        return stamp[11:19]
    dt = datetime.fromisoformat(stamp)
    dt = dt - dt.utcoffset()
    return dt.strftime("%H:%M:%S")

count = 0
for line in lines[1:-1]:
    m = rec.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    stamp, sev, writer, msg = m.groups()
    if sev == "ALARM" and msg.startswith("door-open") and "21:00:00" <= utc_clock(stamp) < "22:00:00":
        count += 1
print(json.dumps({"expected_number": count}))
