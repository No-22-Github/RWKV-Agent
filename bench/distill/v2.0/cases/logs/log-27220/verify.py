# DISTILL-CANARY-099c9b46 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/telemetry-2026-07-12.log"].splitlines()

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
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) writer=(\S+) (.+)$")
lo = datetime.datetime.strptime("2026-07-12 15:30:00", "%Y-%m-%d %H:%M:%S")
hi = datetime.datetime.strptime("2026-07-12 16:15:00", "%Y-%m-%d %H:%M:%S")
value = 0
roam_hits = 0
off_hits = 0
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, probe, writer, msg = m.groups()
    if level != "ERROR" or not msg.startswith("pump stall"):
        continue
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    utc = cur if writer == "hyd-roam" else cur - datetime.timedelta(hours=1)
    if lo <= utc <= hi:
        value += 1
        if writer == "hyd-roam":
            roam_hits += 1
    elif utc < lo and (cur - datetime.timedelta(hours=1)) < lo and writer != "hyd-roam" and cur < lo:
        pass
if roam_hits < 1:
    raise SystemExit("fixture guard failed: roaming targets missing")
early_local = 0
for line in lines[1:-1]:
    m = event_re.match(line)
    if not m or line.startswith("==="):
        continue
    ts, tm, level, probe, writer, msg = m.groups()
    if level == "ERROR" and msg.startswith("pump stall") and writer != "hyd-roam":
        cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
        utc = cur - datetime.timedelta(hours=1)
        if utc < lo:
            early_local += 1
if early_local < 1:
    raise SystemExit("fixture guard failed: pre-window decoys missing")
value
print(json.dumps({"expected_number": value}))
