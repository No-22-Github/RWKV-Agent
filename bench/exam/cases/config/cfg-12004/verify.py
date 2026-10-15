# EXAM-CANARY-9342ad04：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
target = "运行/标本归档.env"
updates = {}
for line in files["交接/审核参数.txt"].splitlines():
    m = re.fullmatch(r"([A-Z_]+)=(.*)", line)
    if m and m.group(2):
        updates[m.group(1)] = m.group(2)
lines = []
for line in files[target].splitlines(keepends=True):
    m = re.fullmatch(r"([A-Z_]+)=([^\n]*)(\n?)", line)
    if m and m.group(1) in updates:
        line = m.group(1) + "=" + updates[m.group(1)] + m.group(3)
    lines.append(line)
result = {target: "".join(lines)}
print(json.dumps({"files": result}, ensure_ascii=False))
