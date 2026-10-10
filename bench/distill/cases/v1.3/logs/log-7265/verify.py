# DISTILL-CANARY-31f44526 : distillation case
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
lines = load_lines("edge-node.log")
n = 0
n_sh = 0
for ln in lines:
    if "回源超时" not in ln:
        continue
    ts = datetime.datetime.fromisoformat(ln.split(" ")[0].replace("Z", "+00:00"))
    bj = ts.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    if bj.date() == datetime.date(2026, 9, 20) and datetime.time(20, 30) <= bj.time() < datetime.time(21, 0):
        n += 1
        if "node=上海节点" in ln:
            n_sh += 1
if n == n_sh:
    raise SystemExit("tz decoy not effective (missing UTC-node events)")
print(json.dumps({"expected_number": n}))
