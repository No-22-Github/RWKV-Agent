# DISTILL-CANARY-e62eb5a9 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/dock-2026-05-19.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) shipment=(\S+) status=(\S+) reason=(.+)$")
rejected_lines = 0
accepted = 0
seen = set()
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, dock, shp, status, reason = m.groups()
    if status == "REJECTED":
        rejected_lines += 1
        seen.add(shp)
    if status == "ACCEPTED":
        accepted += 1
if rejected_lines <= len(seen):
    raise SystemExit("fixture guard failed: re-sent lines missing")
if accepted < 1:
    raise SystemExit("fixture guard failed: accepted rows missing")
value = len(seen)
print(json.dumps({"expected_number": value}))
