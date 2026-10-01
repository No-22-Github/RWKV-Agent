# DISTILL-CANARY-78bec7e0 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/core-2026-06-11.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (INFO|WARN|ERROR) (\S+) req=(\S+) (.+)$")
marker_re = re.compile(r"^=== TRAFFIC SWITCH blue-green completed at \S+ by pipeline \S+ ===$")
markers = [i for i, line in enumerate(lines) if marker_re.match(line)]
if len(markers) != 1:
    raise SystemExit("fixture guard failed: exactly one traffic-switch marker expected")
pre_hits = 0
post_502 = 0
post_warn = 0
value = None
for i, line in enumerate(lines[1:-1], start=1):
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, level, service, req, msg = m.groups()
    if level == "ERROR" and service == "checkout-api" and msg.startswith("upstream code=504"):
        if i < markers[0]:
            pre_hits += 1
        elif value is None:
            value = req
    if level == "ERROR" and msg.startswith("upstream code=502") and i > markers[0]:
        post_502 += 1
    if level == "WARN" and service == "checkout-api" and msg.startswith("upstream code=504"):
        post_warn += 1
if pre_hits < 1 or post_502 < 1 or post_warn < 1 or value is None:
    raise SystemExit("fixture guard failed: decoy or target missing")
print(json.dumps({"expected": value}))
