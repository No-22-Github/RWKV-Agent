# DISTILL-CANARY-158bdf91 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/edi-2026-09-04.log"].splitlines()

head_re = re.compile('^# 岚台海运 EDI 网关日志 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

import datetime
event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 报文=(\S+) (.+)$")
lo = datetime.datetime(2026, 9, 4, 14, 0, 0)
hi = datetime.datetime(2026, 9, 4, 14, 45, 0)
value = 0
april_hits = 0
slash_hits = 0
for line in lines[1:-1]:
    if line.startswith("#"):
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, msg_id, desc = m.groups()
    if level != "ERROR" or not desc.startswith("报文退回"):
        continue
    d, t = ts, tm
    if "/" in d:
        dd, mm, yy = d.split("/")
        cur = datetime.datetime(int(yy), int(mm), int(dd)) + datetime.timedelta(
            hours=int(t[:2]), minutes=int(t[3:5]), seconds=int(t[6:8]))
        if cur.date() == datetime.date(2026, 4, 9):
            april_hits += 1
        if cur.date() == datetime.date(2026, 9, 4):
            slash_hits += 1
    else:
        cur = datetime.datetime.strptime(ts + " " + tm, "%Y-%m-%d %H:%M:%S")
    if lo <= cur <= hi:
        value += 1
if april_hits < 1 or slash_hits < 1:
    raise SystemExit("fixture guard failed: 斜杠批次缺失")
value
print(json.dumps({"expected_number": value}))
