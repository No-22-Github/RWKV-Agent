# DISTILL-CANARY-1a13e5f6 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/booking-2026-08-21.log"].splitlines()

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
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) ref=(\S+) (.+)$")
lo = datetime.datetime(2026, 8, 21, 19, 40, 0)
hi = datetime.datetime(2026, 8, 21, 19, 55, 0)
value = 0
warn_hits = 0
edge_hits = 0
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, ref, msg = m.groups()
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    inwin = lo <= cur <= hi
    if level == "ERROR" and service == "pay-gateway" and msg.startswith("card declined by issuer"):
        if inwin:
            value += 1
        else:
            edge_hits += 1
    if level == "WARN" and msg.startswith("card declined") and inwin:
        warn_hits += 1
if edge_hits < 2 or warn_hits < 1:
    raise SystemExit("fixture guard failed: boundary decoys missing")
value
print(json.dumps({"expected_number": value}))
