# DISTILL-CANARY-6345a420 : distillation case
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

lines = load_lines("media-relay.log")
marker = None
pre_decoy = False
for i, ln in enumerate(lines):
    if "v2.14.0 全量发布完成" in ln:
        marker = i
    if marker is None and " ERROR " in ln and "[混音器]" in ln:
        pre_decoy = True
if marker is None:
    raise SystemExit("release marker not found")
if not pre_decoy:
    raise SystemExit("pre-release mixer ERROR decoy missing")
for ln in lines[marker + 1:]:
    if " ERROR " in ln:
        m = re.search(r"\[(.+?)\]", ln)
        if not m:
            raise SystemExit("post-release ERROR lacks module: " + ln)
        print(json.dumps({"expected_string": m.group(1)}))
        break
else:
    raise SystemExit("no ERROR after marker")
