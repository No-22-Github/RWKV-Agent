# DISTILL-CANARY-3274a9fc : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/resolve-2026-06-02.log"].splitlines()

head_re = re.compile('^=== JOURNAL OPEN host=\\S+ date=\\S+ writers=\\d+ ===$')
close_re = re.compile('^=== JOURNAL CLOSE records=(\\d+) writer=\\S+ ===$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) qid=(\S+) (.+)$")
target = 0
near = 0
for line in lines[1:-1]:
    if line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, node, qid, msg = m.groups()
    if level != "ERROR":
        continue
    if node == "lon-edge-2":
        target += 1
    elif node == "lon-edge-z2":
        near += 1
if near < 1:
    raise SystemExit("fixture guard failed: canary node missing")
value = target
print(json.dumps({"expected_number": value}))
