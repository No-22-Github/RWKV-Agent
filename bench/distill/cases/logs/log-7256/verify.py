# DISTILL-CANARY-514c7715 : distillation case
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

d914 = load_lines("pay-callback-0914.log")
d915 = load_lines("pay-callback-0915.log")
def first_err_channel(lines):
    for ln in lines:
        if " ERROR " in ln:
            m = re.search(r"\[(渠道-[^\]]+)\]", ln)
            if not m:
                raise SystemExit("ERROR line lacks channel: " + ln)
            return m.group(1)
    raise SystemExit("no ERROR line")
warn_decoy = any(" WARN " in ln and "渠道-苏商" in ln for ln in d915)
if not warn_decoy:
    raise SystemExit("WARN decoy missing")
if first_err_channel(d914) != "渠道-淮海":
    raise SystemExit("near-name decoy file changed")
print(json.dumps({"expected_string": first_err_channel(d915)}))
