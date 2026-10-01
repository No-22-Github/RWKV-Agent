# DISTILL-CANARY-6ff047c0 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/lengji-2026-08-30.log"].splitlines()

head_re = re.compile('^# 霜序乳业 冷机日志 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

import datetime
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) writer=(\S+) (.+)$")
value = 0
patrol_prev_day = 0
patrol_next_day = 0
for line in lines[1:-1]:
    if line.startswith("#"):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, unit, writer, desc = m.groups()
    if level != "ERROR" or not desc.startswith("冷机启停失败"):
        continue
    cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    if writer == "patrol-1":
        bj = cur + datetime.timedelta(hours=8)
    else:
        bj = cur
    if bj.strftime("%Y-%m-%d") == "2026-08-30":
        value += 1
        if writer == "patrol-1" and cur.strftime("%Y-%m-%d") == "2026-08-29":
            patrol_prev_day += 1
    elif writer == "patrol-1" and cur.strftime("%Y-%m-%d") == "2026-08-30":
        patrol_next_day += 1
if patrol_prev_day < 1 or patrol_next_day < 1:
    raise SystemExit("fixture guard failed: patrol decoys missing")
value
print(json.dumps({"expected_number": value}))
