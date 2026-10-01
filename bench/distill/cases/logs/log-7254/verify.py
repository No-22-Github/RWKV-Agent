# DISTILL-CANARY-0997b91f : distillation case
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

lines = load_lines("api-ticket.log")
seen = set()
counts = {}
physical = {}
for ln in lines:
    if " ERROR " not in ln:
        continue
    m = re.search(r"\[(.+?)\] id=(TK-\d+)", ln)
    if not m:
        raise SystemExit("ERROR line lacks service/id: " + ln)
    svc, ident = m.group(1), m.group(2)
    physical[svc] = physical.get(svc, 0) + 1
    if ident in seen:
        continue
    seen.add(ident)
    counts[svc] = counts.get(svc, 0) + 1
ranked = sorted(counts.items(), key=lambda kv: -kv[1])
if len(ranked) < 2 or ranked[0][1] == ranked[1][1]:
    raise SystemExit("no unique max service: %s" % ranked)
if physical.get("消息通知", 0) <= counts.get("知识库检索", 0):
    raise SystemExit("dup-row decoy not present")
print(json.dumps({"expected_string": ranked[0][0]}))
