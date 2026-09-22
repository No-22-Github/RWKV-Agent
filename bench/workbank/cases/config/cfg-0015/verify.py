# WORKBANK-CANARY-b2e94d17 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]

overlay_path = "overlays/peak-season.yaml"
active_path = "conf/scheduler.yaml"


def parse_overlay(text):
    values = {}
    order = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        if key not in values:
            order.append(key)
        values[key] = value.strip()
    return values, order


overlay, overlay_order = parse_overlay(files[overlay_path])
if not overlay:
    raise SystemExit("overlay declares no keys")

merged = []
seen = set()
for line in files[active_path].split("\n"):
    stripped = line.strip()
    if stripped and not stripped.startswith("#") and ":" in stripped:
        key = stripped.split(":", 1)[0].strip()
        if key in overlay:
            prefix = line[: len(line) - len(line.lstrip())]
            merged.append(prefix + key + ": " + overlay[key])
            seen.add(key)
            continue
    merged.append(line)

for key in overlay_order:
    if key not in seen:
        merged.append(key + ": " + overlay[key])

content = "\n".join(merged)
print(json.dumps({"files": {active_path: content}}))
