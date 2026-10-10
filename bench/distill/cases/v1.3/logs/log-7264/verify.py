# DISTILL-CANARY-01c694fb : distillation case
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

lines = load_lines("coldchain.log")
first = None
for ln in lines:
    if "高于阈值" not in ln:
        continue
    m = re.search(r"^2026-09-19 (\d{2}):(\d{2}):(\d{2})", ln)
    hh, mm = int(m.group(1)), int(m.group(2))
    if 2 * 60 + 15 <= hh * 60 + mm <= 3 * 60 + 45:
        first = "%02d:%02d" % (hh, mm)
        break
if first is None:
    raise SystemExit("no above-threshold record in window")
print(json.dumps({"expected_string": first}))
