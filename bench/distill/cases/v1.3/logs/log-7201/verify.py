# DISTILL-CANARY-2830735d : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/dispatch-2026-08-22.log"].splitlines()

banner = re.compile(r"^=== RELEASE (\S+) deployed at (\S+) by pipeline (\S+) ===$")
close = re.compile(r"^=== JOURNAL CLOSE records=(\d+) writer=\S+ ===$")
banners = [i for i, line in enumerate(lines) if banner.match(line)]
if len(banners) != 1:
    raise SystemExit("fixture guard failed: exactly one release banner expected")
closes = [i for i, line in enumerate(lines) if close.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event = re.compile(r"^(\S+) (INFO|WARN|ERROR) (\S+) req=(\S+) ")
first = None
for line in lines[banners[0] + 1:-1]:
    m = event.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    if m.group(2) == "ERROR" and m.group(3) == "dispatch-api" and first is None:
        first = m.group(4)
if first is None:
    raise SystemExit("fixture guard failed: no dispatch-api error after the banner")
print(json.dumps({"expected": first}))
