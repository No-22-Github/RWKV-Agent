# DISTILL-CANARY-6ee7d703 : distillation case
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

lines = load_lines("miniapp-api.log")
first = None
for ln in lines:
    if "优惠券核销失败" not in ln:
        continue
    m = re.search(r"^2026-09-22 (\d{2}):(\d{2}):(\d{2})", ln)
    hh, mm = int(m.group(1)), int(m.group(2))
    if 11 * 60 + 30 <= hh * 60 + mm <= 13 * 60:
        first = "%02d:%02d" % (hh, mm)
        break
if first is None:
    raise SystemExit("no redemption failure in window")
print(json.dumps({"expected_string": first}))
