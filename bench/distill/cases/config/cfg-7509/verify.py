# DISTILL-CANARY-4ab83e16 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
props = {}
for line in files["config/relay.properties"].splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, _, value = line.partition("=")
    props[key.strip()] = value.strip()
facts = [props["relay.id"], props["broker.address"], props["max.inflight"]]
print(json.dumps({"expected_contains_any": facts}))
