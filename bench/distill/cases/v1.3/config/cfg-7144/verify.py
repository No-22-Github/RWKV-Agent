# DISTILL-CANARY-8e2471d9 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/pump.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("冲洗时长:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "冲洗时长: 35"
    out.append(line)
print(json.dumps({"files": {"config/pump.yaml": "\n".join(out) + "\n"}}))
