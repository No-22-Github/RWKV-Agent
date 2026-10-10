# DISTILL-CANARY-f3abdb07 : distillation case
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

lines = load_lines("mes-line3.log")
seen = set()
n = 0
phys = 0
old_fmt = 0
next_day = 0
for ln in lines:
    if "急停触发" not in ln:
        continue
    m = re.search(r"流水号=(ES-\d+)", ln)
    if not m:
        raise SystemExit("estop line lacks serial: " + ln)
    phys += 1
    if m.group(1) in seen:
        continue
    seen.add(m.group(1))
    iso = re.match(r"2026-(\d{2})-(\d{2}) ", ln)
    old = re.match(r"\[(\d{2})/(\d{2})/(\d{4}) ", ln)
    if iso:
        if (iso.group(1), iso.group(2)) == ("09", "08"):
            n += 1
        elif (iso.group(1), iso.group(2)) == ("09", "09"):
            next_day += 1
    elif old:
        if (old.group(3), old.group(2), old.group(1)) == ("2026", "09", "08"):
            n += 1
            old_fmt += 1
    else:
        raise SystemExit("unparsed timestamp: " + ln)
if old_fmt == 0:
    raise SystemExit("old-format decoy missing")
if phys == n + next_day:
    raise SystemExit("dup-row decoy missing")
if next_day == 0:
    raise SystemExit("boundary line missing")
print(json.dumps({"expected_number": n}))
