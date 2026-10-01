# DISTILL-CANARY-46e6e676 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/hoist.json"]
out = []
in_main = False
for line in text.splitlines():
    if line.strip().startswith('"提升机"'):
        in_main = True
    elif in_main and line.strip().startswith("}"):
        in_main = False
    if in_main and line.strip().startswith('"上升速度"'):
        line = line.replace("0.8", "1.0")
    out.append(line)
print(json.dumps({"files": {"config/hoist.json": "\n".join(out) + "\n"}}))
