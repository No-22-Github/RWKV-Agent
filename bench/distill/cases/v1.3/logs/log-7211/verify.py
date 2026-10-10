# DISTILL-CANARY-701b48fb : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/shop-2026-04-22.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) trace=(\S+) (.+)$")
marker_re = re.compile(r"^=== POOL DRAIN .+ started at .+ by deployer \S+ ===$")
markers = [i for i, line in enumerate(lines) if marker_re.match(line)]
if len(markers) != 1:
    raise SystemExit("fixture guard failed: exactly one pool-drain banner expected")
pre_hits = 0
post_api_a = 0
post_warn = 0
value = None
for i, line in enumerate(lines[1:-1], start=1):
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, trace, rest = m.groups()
    if service == "edge-proxy" and rest.startswith("origin=api-b code=502"):
        if level == "ERROR":
            if i < markers[0]:
                pre_hits += 1
            elif value is None:
                value = trace
        elif level == "WARN" and i > markers[0]:
            post_warn += 1
    if service == "edge-proxy" and level == "ERROR" and rest.startswith("origin=api-a code=502") and i > markers[0]:
        post_api_a += 1
if pre_hits < 1 or post_api_a < 1 or post_warn < 1 or value is None:
    raise SystemExit("fixture guard failed: decoy or target missing")
print(json.dumps({"expected": value}))
