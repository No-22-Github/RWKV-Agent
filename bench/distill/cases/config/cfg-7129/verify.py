# DISTILL-CANARY-8cd1182a : distillation case
import json

case = json.load(open("case.json"))

def parse_env(text):
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise SystemExit("fixture guard failed: unparsable line " + repr(line))
        values[key.strip()] = value.strip()
    return values

platform = parse_env(case["files"]["deploy/global.env"])
service = parse_env(case["files"]["deploy/harvest-api.env"])

KEY = "MAX_UPLOAD_MB"

# The two layers must conflict on the asked key.
if platform.get(KEY) == service.get(KEY) or KEY not in platform or KEY not in service:
    raise SystemExit("fixture guard failed: the layer conflict is broken")
if "MAINTENANCE_WINDOW" not in platform:
    raise SystemExit("fixture guard failed: global env is broken")

# README.md: the service env overrides the platform global env.
effective = dict(platform)
effective.update(service)
print(json.dumps({"expected_number": int(effective[KEY])}))
