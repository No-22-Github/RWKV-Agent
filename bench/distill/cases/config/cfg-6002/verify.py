# DISTILL-CANARY-db2b4558 : distillation case
import json

case = json.load(open("case.json"))
defaults = json.loads(case["files"]["config/defaults.json"])
overlay = json.loads(case["files"]["config/site-overlay.json"])

# README.md: a key that appears in neither settings layer has no value on
# the depot.
KEY = "compressor_restart_lock_s"
value = "UNKNOWN"
for source in (overlay, defaults):
    if KEY in source:
        value = source[KEY]
        break

print(json.dumps({"expected_string": value}))
