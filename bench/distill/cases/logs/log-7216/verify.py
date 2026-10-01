# DISTILL-CANARY-c64771b9 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/meter-2026-02-17.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|CRITICAL) (\S+) meter=(\S+) (.+)$")
tally_re = re.compile(r"^# day-shift tally \S+ - sensor drop events entered so far = (\d+) \(operator \S+\)$")
value = 0
tallies = []
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    t = tally_re.match(line)
    if t:
        tallies.append(int(t.group(1)))
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, meter, msg = m.groups()
    if level == "CRITICAL" and msg.startswith("sensor drop"):
        value += 1
if len(tallies) != 1 or tallies[0] == value:
    raise SystemExit("fixture guard failed: tally line malformed or equal to the true count")
other_critical = 0
for line in lines[1:-1]:
    m = event_re.match(line)
    if m and m.group(3) == "CRITICAL" and not m.group(6).startswith("sensor drop"):
        other_critical += 1
if other_critical < 1:
    raise SystemExit("fixture guard failed: other CRITICAL lines missing")
print(json.dumps({"expected_number": value}))
