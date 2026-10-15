# EXAM-CANARY-a638bf04：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
fields_by_name = {}
for line in files["接口/展品借调说明.md"].splitlines():
    if line.startswith("字段="):
        fields = dict(x.split("=", 1) for x in line.split("｜"))
        omission = fields["可省略"]
        fields["提交条件"] = "必填" if omission == "否" else "选填" if omission == "是" else "条件必填"
        fields["场景"] = omission
        fields_by_name[fields["字段"]] = fields
path = "联调/借调字段核对表.md"
result = {path: re.sub(r"\{\{([^.{}]+)\.([^{}]+)\}\}", lambda m: fields_by_name[m.group(1)][m.group(2)], files[path])}
print(json.dumps({"files": result}, ensure_ascii=False))
