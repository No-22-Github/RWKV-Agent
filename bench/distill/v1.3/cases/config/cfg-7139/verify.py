# DISTILL-CANARY-bb5ce62d : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/repair-desk.json"]

out = []
changed = 0
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith('"auto_close_days"'):
        line = line.replace("7", "10")
        changed += 1
    out.append(line)

if changed != 1:
    raise SystemExit("fixture guard failed: auto_close_days line count " + str(changed))
if '"desk": "muye-repair-desk"' not in text:
    raise SystemExit("fixture guard failed: repair-desk.json is broken")

print(json.dumps({"files": {"config/repair-desk.json": "\n".join(out) + "\n"}}))
