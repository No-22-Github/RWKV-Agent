# DISTILL-CANARY-5075834e : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/cdn-2026-07-14.log"].splitlines()

head_re = re.compile('^# 双屿数联 回源日志 \\S+ 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 节点=(\S+) (.+)$")
target = 0
near = 0
for line in lines[1:-1]:
    if line.startswith("#"):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, node, desc = m.groups()
    if level != "ERROR":
        continue
    if node == "edge-cw-01":
        target += 1
    elif node == "edge-cw-l01":
        near += 1
if near < 1:
    raise SystemExit("fixture guard failed: 近名节点缺失")
value = target
print(json.dumps({"expected_number": value}))
