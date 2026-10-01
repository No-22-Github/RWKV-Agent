# DISTILL-CANARY-7e475e59 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/boiler-2-schedule.yaml"]
out = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("preheat_minutes:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "preheat_minutes: 55"
    out.append(line)
print(json.dumps({"files": {"config/boiler-2-schedule.yaml": "\n".join(out) + "\n"}}))
