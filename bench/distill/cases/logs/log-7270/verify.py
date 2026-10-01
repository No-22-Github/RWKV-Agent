# DISTILL-CANARY-3cb3de0e : distillation case
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

lines = load_lines("rider-trace.jsonl")
fees = []
dirty = 0
for ln in lines:
    r = json.loads(ln)
    if r.get("状态") != "已结算":
        continue
    fee = r.get("配送费")
    if isinstance(fee, bool) or not isinstance(fee, (int, float)):
        dirty += 1
        continue
    fees.append(fee)
if dirty == 0:
    raise SystemExit("dirty settled rows missing")
if len(fees) == 0:
    raise SystemExit("no valid settled fee")
print(json.dumps({"expected_number": sum(fees) / len(fees)}))
