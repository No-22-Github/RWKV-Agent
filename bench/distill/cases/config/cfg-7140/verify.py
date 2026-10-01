# DISTILL-CANARY-dd1bc574 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/kiln.yaml"]

out = []
changed = 0
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("hold_hours:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "hold_hours: 8"
        changed += 1
    out.append(line)

if changed != 1:
    raise SystemExit("fixture guard failed: hold_hours line count " + str(changed))
if "max_temp_c" not in text:
    raise SystemExit("fixture guard failed: kiln.yaml is broken")

print(json.dumps({"files": {"config/kiln.yaml": "\n".join(out) + "\n"}}))
