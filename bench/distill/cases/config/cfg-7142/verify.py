# DISTILL-CANARY-597526c8 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/gate.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("hold_open_s:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "hold_open_s: 45"
    out.append(line)
print(json.dumps({"files": {"config/gate.yaml": "\n".join(out) + "\n"}}))
