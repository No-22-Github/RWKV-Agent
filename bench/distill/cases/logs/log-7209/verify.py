# DISTILL-CANARY-99762326 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/relay-2026-08-05.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) job=(\S+) (.+)$")
open_re = re.compile(r"^=== MAINT WINDOW OPEN .+ feeder \S+ crew \S+ ===$")
close_re = re.compile(r"^=== MAINT WINDOW CLOSE .+ feeder \S+ crew \S+ ===$")
opens = [i for i, line in enumerate(lines) if open_re.match(line)]
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if len(opens) != 1 or len(closes) != 1 or closes[0] < opens[0]:
    raise SystemExit("fixture guard failed: maintenance banners malformed")
value = None
warn_seen = False
for i, line in enumerate(lines[1:opens[0]], start=1):
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, job, msg = m.groups()
    if level == "ERROR" and service == "feeder-relay" and msg.startswith("breaker telemetry rejected"):
        value = job
    if level == "WARN" and service == "feeder-relay":
        warn_seen = True
after = 0
for line in lines[closes[0] + 1:-1]:
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, service, job, msg = m.groups()
    if level == "ERROR" and service == "feeder-relay" and msg.startswith("breaker telemetry rejected"):
        after += 1
if value is None or not warn_seen or after < 2:
    raise SystemExit("fixture guard failed: decoy or target missing")
print(json.dumps({"expected": value}))
