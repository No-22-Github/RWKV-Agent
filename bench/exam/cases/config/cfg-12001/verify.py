# EXAM-CANARY-9342ad01：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
path = "设置/口述转写.ini"
text = files[path]
seconds = int(re.search(r"改为 (\d+) 秒", case["turns"][0]["prompt"]).group(1))
result = {path: re.sub(r"(?m)^(autosave_seconds = )\d+$", lambda m: m.group(1) + str(seconds), text)}
print(json.dumps({"files": result}, ensure_ascii=False))
