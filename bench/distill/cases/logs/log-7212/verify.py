# DISTILL-CANARY-3d072427 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/zhuang-2026-09-02.log"].splitlines()

head_re = re.compile('^# 铁马充电 充电桩日志 \\S+ 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 桩号=(\S+) 网点=(\S+) (.+)$")
marker_re = re.compile(r"^=== 桩联网关升级完成 .+ 版本 \S+ ===$")
markers = [i for i, line in enumerate(lines) if marker_re.match(line)]
if len(markers) != 1:
    raise SystemExit("fixture guard failed: 升级标记应恰好一条")
pre_hits = 0
near_hits = 0
warn_hits = 0
value = None
for i, line in enumerate(lines[1:-1], start=1):
    if line.startswith("#") or line.startswith("==="):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, z, wh, desc = m.groups()
    if wh == "H-217" and desc.startswith("回执超时"):
        if level == "ERROR":
            if i < markers[0]:
                pre_hits += 1
            elif value is None:
                value = z
        elif level == "WARN" and i > markers[0]:
            warn_hits += 1
    if wh == "H-118" and desc.startswith("回执超时") and i > markers[0]:
        near_hits += 1
if pre_hits < 1 or near_hits < 1 or warn_hits < 1 or value is None:
    raise SystemExit("fixture guard failed: decoy or target missing")
print(json.dumps({"expected": value}))
