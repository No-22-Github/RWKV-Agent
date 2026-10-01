# DISTILL-CANARY-6d8fe593 : distillation case
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

lines = load_lines("exam-api.log")
text = "\n".join(lines)
if "code=E5012" not in text:
    raise SystemExit("E5012 failures missing")
if "code=E4031" not in text:
    raise SystemExit("E4031 noise missing")
if "心跳丢失" in text:
    cause = "阅卷引擎过载"
else:
    cause = "考生网络异常"
print(json.dumps({"expected_string": cause}))
