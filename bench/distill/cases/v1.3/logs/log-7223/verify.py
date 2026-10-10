# DISTILL-CANARY-42eb31a6 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/stream-2026-05-06.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

import datetime
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) region=(\S+) (.+)$")
lo = datetime.datetime(2026, 5, 6, 21, 0, 0)
hi = datetime.datetime(2026, 5, 6, 21, 30, 0)
value = 0
near_hits = 0
edge_hits = 0
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, region, msg = m.groups()
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    inwin = lo <= cur <= hi
    if level == "ERROR" and msg.startswith("session lease lost"):
        if service == "pay-sim":
            if inwin:
                value += 1
            else:
                edge_hits += 1
        elif service == "pay-sim-eu" and inwin:
            near_hits += 1
if near_hits < 1 or edge_hits < 2:
    raise SystemExit("fixture guard failed: decoys missing")
value
print(json.dumps({"expected_number": value}))
