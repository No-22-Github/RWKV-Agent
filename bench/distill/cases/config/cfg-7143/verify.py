# DISTILL-CANARY-c5257b71 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/boiler.yaml"]
out = []
section = ""
for line in text.splitlines():
    stripped = line.strip()
    if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#") and stripped.endswith(":"):
        section = stripped[:-1]
    if section == "泡池区" and stripped.startswith("供水温度:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "供水温度: 44"
    out.append(line)
print(json.dumps({"files": {"config/boiler.yaml": "\n".join(out) + "\n"}}))
