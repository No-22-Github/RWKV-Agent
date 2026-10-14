# DISTILL-CANARY-c0731e7f : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/chargers.yaml"]
out = []
section = ""
for line in text.splitlines():
    stripped = line.strip()
    if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#") and stripped.endswith(":"):
        section = stripped[:-1]
    if section == "spill_yard" and stripped.startswith("session_limit_kw:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "session_limit_kw: 80"
    out.append(line)
print(json.dumps({"files": {"config/chargers.yaml": "\n".join(out) + "\n"}}))
