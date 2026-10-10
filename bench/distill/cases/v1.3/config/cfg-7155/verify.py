# DISTILL-CANARY-0a4a1cc6 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/boiler-schedule.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("setback_temp_c:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "setback_temp_c: 63"
    out.append(line)
print(json.dumps({"files": {"config/boiler-schedule.yaml": "\n".join(out) + "\n"}}))
