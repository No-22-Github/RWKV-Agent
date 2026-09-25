# DISTILL-CANARY-47c9b1e6 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/frame-settings.yaml"]

# README.md: the frame reads its settings from this file when a run starts.
values = {}
for line in text.splitlines():
    key, _, raw = line.partition(":")
    values[key.strip()] = raw.strip()

print(json.dumps({"expected_number": int(values["creel_bobbins"])}))
