# DISTILL-CANARY-b63ed4ee : distillation case
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

lines = load_lines("im-server.log")
reason = None
n = 0
for ln in lines:
    if " ERROR " not in ln or "[消息投递]" not in ln:
        continue
    m = re.search(r"发送失败：(\S+)", ln)
    if not m:
        raise SystemExit("delivery ERROR lacks stated reason: " + ln)
    if reason is None:
        reason = m.group(1)
    elif m.group(1) != reason:
        raise SystemExit("multiple stated reasons: " + reason + " / " + m.group(1))
    n += 1
if n < 3:
    raise SystemExit("too few delivery ERROR lines")
print(json.dumps({"expected_string": reason}))
