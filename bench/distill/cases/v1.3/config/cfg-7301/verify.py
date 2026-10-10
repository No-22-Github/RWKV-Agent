# DISTILL-CANARY-62c0fa84 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/capture.yaml"]
out_lines = []
section = ""
for line in text.splitlines():
    stripped = line.strip()
    if stripped and not line.startswith(" ") and not stripped.startswith("#") and stripped.endswith(":"):
        section = stripped[:-1]
    if section == "capture" and stripped.startswith("burst_count:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "burst_count: 8"
    out_lines.append(line)
print(json.dumps({"files": {"config/capture.yaml": "\n".join(out_lines) + "\n"}}))
