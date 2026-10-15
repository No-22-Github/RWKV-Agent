# EXAM-CANARY-a638bf01：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
items = {}
for line in files["交班/巡馆安排.md"].splitlines():
    parts = line.split("｜")
    if parts[0] == "已确认":
        fields = dict(s.split("=", 1) for s in parts[1:])
        items[fields["编号"]] = fields
path = "导入/巡馆排班.csv"
result = {path: re.sub(r"\{\{(G\d+)(姓名|时段|区域)\}\}", lambda m: items[m.group(1)][m.group(2)], files[path])}
print(json.dumps({"files": result}, ensure_ascii=False))
