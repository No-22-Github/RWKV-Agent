# DISTILL-CANARY-8538ce8e : distillation case
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

lines = load_lines("api-gateway.log")
for ln in lines:
    if " ERROR " in ln:
        m = re.search(r"(?:GET|POST|PUT|DELETE) (\/\S+)", ln)
        if not m:
            raise SystemExit("first ERROR line has no request path: " + ln)
        print(json.dumps({"expected_string": m.group(1)}))
        break
else:
    raise SystemExit("no ERROR line found")
