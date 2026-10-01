# DISTILL-CANARY-40c1f43a : distillation case
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
lines = load_lines("gift-stream.jsonl")
total = 0.0
pre = 0
cut = datetime.datetime.fromisoformat("2026-09-24T20:00:00+08:00")
for ln in lines:
    r = json.loads(ln)
    if r.get("礼物") != "浪漫烟花":
        continue
    ts = datetime.datetime.fromisoformat(r["时间"])
    if ts < cut:
        pre += 1
        continue
    total += r["收益"]
if pre == 0:
    raise SystemExit("pre-show decoy rows missing")
print(json.dumps({"expected_number": round(total, 2)}))
