# WORKBANK-CANARY-e08b3a6c : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]


def parse_section(text, section):
    values = {}
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            inside = stripped.endswith(":") and stripped[:-1].strip() == section
            continue
        if inside and ":" in stripped:
            key, _, value = stripped.partition(":")
            values[key.strip()] = value.strip()
    return values


def parse_flat(text):
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        values[key.strip()] = value.strip()
    return values


defaults = parse_section(files["deploy/defaults.yaml"], "dispatch-router")
local = parse_section(files["deploy/local.yaml"], "dispatch-router")
staging_overlay = parse_flat(files["deploy/staging/dispatch-router.yaml"])

key = "hold_queue_depth"
if key in staging_overlay:
    effective = int(staging_overlay[key])
elif key in local:
    effective = int(local[key])
elif key in defaults:
    effective = int(defaults[key])
else:
    raise SystemExit("hold_queue_depth not found in any layer")
print(json.dumps({"expected_number": effective}))
