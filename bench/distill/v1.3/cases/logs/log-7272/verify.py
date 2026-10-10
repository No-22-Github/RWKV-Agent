# DISTILL-CANARY-e62e7840 : distillation case
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

lines = load_lines("audit-ops.jsonl")
seen = set()
n = 0
phys = 0
for ln in lines:
    r = json.loads(ln)
    if r.get("操作") != "外链分享撤销":
        continue
    phys += 1
    rid = r.get("请求号")
    if not rid:
        raise SystemExit("revoke record lacks request id: " + ln)
    if rid in seen:
        continue
    seen.add(rid)
    n += 1
if phys == n:
    raise SystemExit("dup-row decoy not present")
print(json.dumps({"expected_number": n}))
