# DISTILL-CANARY-8995929a : distillation case
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

lines = load_lines("robot-sched.log")
started, failed, ok = {}, set(), set()
daily = None
for ln in lines:
    if "[日报]" in ln:
        if "成功率 100%" not in ln:
            raise SystemExit("daily report claim changed")
        daily = ln
        continue
    m = re.search(r"机器人 (R-\d+)", ln)
    if not m:
        continue
    rid = m.group(1)
    if "开始充电对接" in ln:
        started[rid] = True
    if "充电对接失败" in ln:
        failed.add(rid)
    if "充电正常" in ln:
        ok.add(rid)
if daily is None:
    raise SystemExit("daily report line missing")
bad = sorted(rid for rid in failed if rid not in ok)
if bad != ["R-07"]:
    raise SystemExit("unexpected failed robots: %s" % bad)
if "R-03" not in ok:
    raise SystemExit("R-03 scare decoy missing")
print(json.dumps({"expected_string": bad[0]}))
