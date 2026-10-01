# DISTILL-CANARY-6a93fea9 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/irrigation.yaml"]
out = []
section = ""
for line in text.splitlines():
    stripped = line.strip()
    if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#") and stripped.endswith(":"):
        section = stripped[:-1]
    if section == "drip_lines" and stripped.startswith("run_pressure_bar:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "run_pressure_bar: 1.4"
    out.append(line)
print(json.dumps({"files": {"config/irrigation.yaml": "\n".join(out) + "\n"}}))
