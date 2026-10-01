# DISTILL-CANARY-997a4e3d : distillation case
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

import datetime
sh = load_lines("checkin-shanghai.jsonl")
ld = load_lines("checkin-london.jsonl")
bj = datetime.timezone(datetime.timedelta(hours=8))
n = 0
n_sh = 0
for lines, is_utc in ((sh, False), (ld, True)):
    for ln in lines:
        r = json.loads(ln)
        if r.get("类型") != "团课签到":
            continue
        ts = datetime.datetime.fromisoformat(r["时间"].replace("Z", "+00:00")).astimezone(bj)
        if ts.date() == datetime.date(2026, 9, 26):
            n += 1
            if not is_utc:
                n_sh += 1
if n == n_sh:
    raise SystemExit("multisrc/tz decoy not effective (london rows missing)")
print(json.dumps({"expected_number": n}))
