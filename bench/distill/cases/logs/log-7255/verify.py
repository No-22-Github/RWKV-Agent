# DISTILL-CANARY-c2f251dc : distillation case
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

lines = load_lines("device-event.log")
first = None
first_upper = None
for ln in lines:
    m = re.search(r"级别=(\S+)", ln)
    if not m:
        continue
    lvl = m.group(1)
    if lvl in ("ERROR", "error"):
        m2 = re.search(r"锁编号=(SL-\d+)", ln)
        if not m2:
            raise SystemExit("error-level line lacks lock id: " + ln)
        if first is None:
            first = m2.group(1)
        if lvl == "ERROR" and first_upper is None:
            first_upper = m2.group(1)
if first is None:
    raise SystemExit("no error-level line found")
if first_upper == first:
    raise SystemExit("missing-level decoy not effective")
print(json.dumps({"expected_string": first}))
