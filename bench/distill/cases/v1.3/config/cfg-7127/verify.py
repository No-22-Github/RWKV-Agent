# DISTILL-CANARY-24b8de8a : distillation case
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

service = parse_env(case["files"]["deploy/mill-api.env"])
platform = parse_env(case["files"]["deploy/global.env"])

KEY = "LOG_FLUSH_SECONDS"

# Premise: the asked key is set only in the platform layer...
if KEY in service:
    raise SystemExit("fixture guard failed: " + KEY + " leaked into the service env")
if KEY not in platform:
    raise SystemExit("fixture guard failed: " + KEY + " missing from global env")
# ...and the service env stays load-bearing for its own keys.
if "MILL_API_WORKERS" not in service:
    raise SystemExit("fixture guard failed: service env is broken")

effective = dict(platform)
effective.update(service)
print(json.dumps({"expected_number": int(effective[KEY])}))
