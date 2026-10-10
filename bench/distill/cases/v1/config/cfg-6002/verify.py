# DISTILL-CANARY-db2b4558 : distillation case
import json

case = json.load(open("case.json"))
overlay = json.loads(case["files"]["config/site-overlay.json"])
defaults = json.loads(case["files"]["config/defaults.json"])

# README.md: a key that appears in neither settings layer has no value on
# the depot. The case asserts that no layer defines the key; recompute that
# here from both files.
KEY = "compressor_restart_lock_s"
for name, source in (("config/site-overlay.json", overlay), ("config/defaults.json", defaults)):
    if KEY in source:
        raise SystemExit(name + " now defines " + KEY + "; the absent-object case is broken")

accepted = [
    "compressor_restart_lock_s",
    "compressor restart lock",
    "restart lock",
]
print(json.dumps({"expected_contains_any": accepted}))
