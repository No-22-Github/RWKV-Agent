# DISTILL-CANARY-1de95b70 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/dispatch-relay.yaml"]

settings = {}
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, _, value = line.partition(":")
    settings[key.strip()] = value.strip()

window_ms = int(settings["keepalive_window_ms"])

print(json.dumps({"expected_number": window_ms / 1000}))
