# DISTILL-CANARY-a89b4baf : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/decoction.yaml"]
out = []
section = ""
for line in text.splitlines():
    stripped = line.strip()
    if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#") and stripped.endswith(":"):
        section = stripped[:-1]
    if section == "二号机" and stripped.startswith("先煎分钟:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "先煎分钟: 35"
    out.append(line)
print(json.dumps({"files": {"config/decoction.yaml": "\n".join(out) + "\n"}}))
