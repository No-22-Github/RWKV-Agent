# DISTILL-CANARY-371b62d0 : distillation case
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

d911 = load_lines("sorter-0911.log")
d912 = load_lines("sorter_0912.log")
def first_missort(lines):
    for ln in lines:
        if " ERROR " in ln and "错分" in ln:
            m = re.search(r"滑槽(S-\d{2})", ln)
            if not m:
                raise SystemExit("missort line lacks chute: " + ln)
            return m.group(1)
    raise SystemExit("no missort ERROR found")
decoy = first_missort(d911)
ans = first_missort(d912)
if decoy == ans:
    raise SystemExit("near-name decoy must differ from answer")
print(json.dumps({"expected_string": ans}))
