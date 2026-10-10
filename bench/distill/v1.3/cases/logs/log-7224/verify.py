# DISTILL-CANARY-9ac5bb40 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/press-2026-04-03.log"].splitlines()

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
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) job=(\S+) (.+)$")
lo = datetime.datetime(2026, 4, 3, 22, 10, 0)
hi = datetime.datetime(2026, 4, 3, 22, 40, 0)
raw = 0
seen = set()
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, job, msg = m.groups()
    if level != "ERROR" or service != "queue-mgr" or not msg.startswith("queue flood"):
        continue
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    if lo <= cur <= hi:
        raw += 1
        seen.add(job)
if raw <= len(seen):
    raise SystemExit("fixture guard failed: re-sent lines missing")
value = len(seen)
print(json.dumps({"expected_number": value}))
