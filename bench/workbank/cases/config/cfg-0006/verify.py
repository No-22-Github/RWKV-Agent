# WORKBANK-CANARY-b41e08f2 : bank artifact, excluded from training corpora
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


def parse_env(text):
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


defaults = parse_section(files["config/default.yaml"], "parcel_sorter")
local = parse_section(files["config/local.yaml"], "parcel_sorter")
env = parse_env(files["environments/qa.env"])

key = "max_inflight_batches"
env_key = "PARCEL_SORTER_MAX_INFLIGHT_BATCHES"
if env_key in env:
    effective = int(env[env_key])
elif key in local:
    effective = int(local[key])
elif key in defaults:
    effective = int(defaults[key])
else:
    raise SystemExit("max_inflight_batches not found in any layer")
print(json.dumps({"expected_number": effective}))
