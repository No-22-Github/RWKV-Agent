# DISTILL-CANARY-9afe7543 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/fenbo-2026-08-30.log"].splitlines()

head_re = re.compile('^# 雁回物流 分播日志 \\S+ 采集器 \\S+$')
close_re = re.compile('^# 日志收播 记录数=(\\d+) 采集器=\\S+$')
if not head_re.match(lines[0]) or any(head_re.match(line) for line in lines[1:]):
    raise SystemExit("fixture guard failed: journal head must be line 1 and unique")
closes = [i for i, line in enumerate(lines) if close_re.match(line)]
if closes != [len(lines) - 1]:
    raise SystemExit("fixture guard failed: journal close must be the last line")
if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: record count does not match the close line")

event_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) 波次=(\S+) (.+)$")
tally_re = re.compile(r"^# 昨日汇总 \S+：拣选异常告警 (\d+) 条（值班 \S+）$")
raw = 0
seen = set()
tallies = []
for line in lines[1:-1]:
    if line.startswith("#"):
        t = tally_re.match(line)
        if t:
            tallies.append(int(t.group(1)))
        continue
    m = event_re.match(line)
    if not m:
        raise SystemExit("unreadable journal line: " + line)
    ts, tm, level, wave, desc = m.groups()
    if level == "ERROR" and desc.startswith("拣选异常"):
        raw += 1
        seen.add(wave)
if raw <= len(seen):
    raise SystemExit("fixture guard failed: 重发行缺失")
if len(tallies) != 1 or tallies[0] == len(seen):
    raise SystemExit("fixture guard failed: 昨日汇总行异常")
value = len(seen)
print(json.dumps({"expected_number": value}))
