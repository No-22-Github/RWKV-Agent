# DISTILL-CANARY-dc0b98b7 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/playout.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("retention_days:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "retention_days: 45"
    out.append(line)
print(json.dumps({"files": {"config/playout.yaml": "\n".join(out) + "\n"}}))
