# DISTILL-CANARY-3f7c1a92 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/benchsched.yaml"]

settings = {}
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, _, value = line.partition(":")
    settings[key.strip()] = value.strip()

print(json.dumps({"expected_number": int(settings["queue_capacity"])}))
