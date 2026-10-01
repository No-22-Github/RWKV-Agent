# DISTILL-CANARY-0e1b11bb : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/lenglian-2026-07-08.log"].splitlines()

head_re = re.compile('^# 海雾冷链 运输监测日志 \\S+ 汇聚网关 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 网关=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 终端=(\S+) (.+)$")
marker_re = re.compile(r"^=== 巡检窗口开始 \S+ \S+ 负责人 \S+ ===$")
markers = [i for i, line in enumerate(lines) if marker_re.match(line)]
if len(markers) != 1:
    raise SystemExit("fixture guard failed: 巡检开始标记应恰好一条")
pre_hits = 0
post_warn = 0
value = None
for i, line in enumerate(lines[1:-1], start=1):
    if line.startswith("#") or line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, tj, desc = m.groups()
    if level == "ERROR" and desc.startswith("温控超限"):
        if i < markers[0]:
            pre_hits += 1
        elif value is None:
            value = tj
    if level == "WARN" and desc.startswith("温控超限") and i > markers[0]:
        post_warn += 1
if pre_hits < 1 or post_warn < 1 or value is None:
    raise SystemExit("fixture guard failed: decoy or target missing")
print(json.dumps({"expected": value}))
