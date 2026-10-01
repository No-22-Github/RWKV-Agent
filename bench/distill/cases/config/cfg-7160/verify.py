# DISTILL-CANARY-88653f55 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/station.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("免费时长分钟:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "免费时长分钟: 45"
    out.append(line)
print(json.dumps({"files": {"config/station.yaml": "\n".join(out) + "\n"}}))
