# EXAM-CANARY-9342ad03：独立重算参考终态
import json
import re
from pathlib import Path

case = json.loads(Path("case.json").read_text(encoding="utf-8"))
files = case["files"]
path = "设备/机械臂.toml"
angle = re.search(r"改为 ([0-9.]+) 度", case["turns"][0]["prompt"]).group(1)
section = None
lines = []
for line in files[path].splitlines(keepends=True):
    if line.startswith("["):
        section = line.strip()[1:-1]
    if section == "teaching" and re.match(r"^step_degrees\s*=", line):
        line = re.sub(r"(=\s*)[0-9.]+", lambda m: m.group(1) + angle, line)
    lines.append(line)
result = {path: "".join(lines)}
print(json.dumps({"files": result}, ensure_ascii=False))
