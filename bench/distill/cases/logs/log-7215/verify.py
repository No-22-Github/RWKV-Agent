# DISTILL-CANARY-4701d191 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/kiln-2026-03-08.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) batch=(\S+) (.+)$")
raw = 0
warn_margin = 0
seen = set()
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, kiln, batch, msg = m.groups()
    if level == "ERROR" and msg.startswith("kiln overheat alarm"):
        raw += 1
        seen.add(batch)
    if level == "WARN" and msg.startswith("kiln overheat margin low"):
        warn_margin += 1
if raw <= len(seen):
    raise SystemExit("fixture guard failed: re-sent lines missing")
if warn_margin < 1:
    raise SystemExit("fixture guard failed: overheat-margin WARN missing")
value = len(seen)
print(json.dumps({"expected_number": value}))
