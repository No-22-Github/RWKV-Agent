# DISTILL-CANARY-df0cf9d0 : distillation case
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

lines = load_lines("sync-stock.log")
seen = set()
real = 0
phys = 0
for ln in lines:
    if "库存不一致" not in ln:
        continue
    m = re.search(r"流水号=(SY-\d+)", ln)
    if not m:
        raise SystemExit("mismatch line lacks serial: " + ln)
    phys += 1
    if m.group(1) in seen:
        continue
    seen.add(m.group(1))
    real += 1
if phys == real:
    raise SystemExit("dup-row decoy not present")
print(json.dumps({"expected_number": real}))
