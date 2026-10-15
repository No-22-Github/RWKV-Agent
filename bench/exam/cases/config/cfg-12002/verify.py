# EXAM-CANARY-9342ad02：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
path = "终端/签到屏.env"
brightness = re.search(r"待机亮度改成 (\d+)", case["turns"][0]["prompt"]).group(1)
result = {path: re.sub(r"(?m)^IDLE_BRIGHTNESS=\d+$", "IDLE_BRIGHTNESS=" + brightness, files[path])}
print(json.dumps({"files": result}, ensure_ascii=False))
