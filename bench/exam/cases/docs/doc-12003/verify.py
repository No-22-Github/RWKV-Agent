# EXAM-CANARY-a638bf03：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
versions = []
for line in files["发布/借阅终端方案.md"].splitlines():
    if line.startswith("版本="):
        fields = dict(x.split("=", 1) for x in line.split("｜"))
        if fields["状态"] == "现行":
            versions.append(fields)
if len(versions) != 1:
    raise ValueError("现行方案必须恰有一份")
path = "服务台/借阅发布卡.md"
result = {path: re.sub(r"\{\{([^{}]+)\}\}", lambda m: versions[0][m.group(1)], files[path])}
print(json.dumps({"files": result}, ensure_ascii=False))
