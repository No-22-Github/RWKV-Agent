# DISTILL-CANARY-2928f4a5 : distillation case
import json
import re

case = json.load(open("case.json"))
FILES = case["files"]

FOOTER_RE = re.compile(r"共 (\d+) 行")

def load_lines(name):
    """读取一个日志夹具并校验完整性页脚，返回不含页脚的行列表。"""
    text = FILES[name]
    lines = text.split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        raise SystemExit("fixture %s is empty" % name)
    m = FOOTER_RE.search(lines[-1])
    if not m:
        raise SystemExit("fixture %s: last line is not a footer" % name)
    if int(m.group(1)) != len(lines) - 1:
        raise SystemExit("fixture %s: footer claims %s lines, has %d" % (name, m.group(1), len(lines) - 1))
    return lines[:-1]

import datetime
o_lines = load_lines("orders-api.log")
p_lines = load_lines("payments-api.log")
events = []
for lines in (o_lines, p_lines):
    for ln2 in lines:
        if "库存扣减失败" not in ln2:
            continue
        ts = datetime.datetime.fromisoformat(ln2.split(" ")[0].replace("Z", "+00:00"))
        bj = ts.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        if bj.date() == datetime.date(2026, 9, 21) and datetime.time(10, 0) <= bj.time() < datetime.time(10, 20):
            events.append((bj, ln2))
events.sort(key=lambda e: e[0])
if not events:
    raise SystemExit("no deduction failure in window")
first = events[0][0].strftime("%H:%M")
if first != "10:03":
    raise SystemExit("unexpected first event: " + first)
times = {e[0].strftime("%H:%M") for e in events}
if "10:14" not in times or "10:19" not in times:
    raise SystemExit("decoy events missing")
print(json.dumps({"expected_string": first}))
