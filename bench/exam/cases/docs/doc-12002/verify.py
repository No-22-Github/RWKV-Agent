# EXAM-CANARY-a638bf02：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
steps = {}
for line in files["规程/水样接收说明.md"].splitlines():
    parts = line.split("｜")
    if parts[0] == "正式环节":
        fields = dict(x.split("=", 1) for x in parts[1:])
        steps[fields["名称"]] = fields
path = "现场/水样流程卡.md"
result = {path: re.sub(r"\{\{([^.{}]+)\.([^{}]+)\}\}", lambda m: steps[m.group(1)][m.group(2)], files[path])}
print(json.dumps({"files": result}, ensure_ascii=False))
