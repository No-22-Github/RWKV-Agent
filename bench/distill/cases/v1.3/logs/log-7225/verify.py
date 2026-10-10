# DISTILL-CANARY-6d2f3561 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/wendu-2026-01-19.log"].splitlines()

head_re = re.compile('^# 竹隐家居 温控日志 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

import datetime
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 库区=(\S+) writer=(\S+) (.+)$")
lo = datetime.datetime(2026, 1, 19, 20, 0, 0)
hi = datetime.datetime(2026, 1, 19, 21, 0, 0)
raw = 0
seen = set()
patrol_decoy = 0
for line in lines[1:-1]:
    if line.startswith("#"):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, zone, writer, desc = m.groups()
    if level != "ERROR" or not desc.startswith("低温告警"):
        continue
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    bj = cur + datetime.timedelta(hours=8) if writer == "patrol-1" else cur
    if writer == "patrol-1" and cur.strftime("%H") in ("20", "21") and bj.date() != datetime.date(2026, 1, 19):
        patrol_decoy += 1
    if lo <= bj <= hi:
        raw += 1
        seen.add(zone)
if raw <= len(seen):
    raise SystemExit("fixture guard failed: 重发行缺失")
if patrol_decoy < 1:
    raise SystemExit("fixture guard failed: patrol 换日 decoy 缺失")
value = len(seen)
print(json.dumps({"expected_number": value}))
