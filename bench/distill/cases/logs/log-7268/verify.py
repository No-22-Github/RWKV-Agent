# DISTILL-CANARY-7d7038a7 : distillation case
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

lines = load_lines("booking-api.log")
n = 0
n_iso = 0
for ln in lines:
    if "号源锁定失败" not in ln:
        continue
    iso = re.match(r"2026-09-23 (\d{2}):(\d{2}):(\d{2})", ln)
    old = re.match(r"\[23/09/2026 (\d{2}):(\d{2}):(\d{2})\]", ln)
    if iso:
        hh = int(iso.group(1))
        if hh == 8:
            n += 1
            n_iso += 1
    elif old:
        hh = int(old.group(1))
        if hh == 8:
            n += 1
    else:
        raise SystemExit("unparsed timestamp: " + ln)
if n == n_iso:
    raise SystemExit("date-format decoy not effective")
print(json.dumps({"expected_number": n}))
