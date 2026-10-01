# DISTILL-CANARY-d5432f0f : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/drying.yaml"]

out = []
changed = 0
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("cooling_minutes:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "cooling_minutes: 90"
        changed += 1
    out.append(line)

if changed != 1:
    raise SystemExit("fixture guard failed: cooling_minutes line count " + str(changed))
if "target_moisture_pct" not in text:
    raise SystemExit("fixture guard failed: drying.yaml is broken")

print(json.dumps({"files": {"config/drying.yaml": "\n".join(out) + "\n"}}))
