# DISTILL-CANARY-d0357d5e : distillation case
import json

case = json.load(open("case.json"))
services = json.loads(case["files"]["config/services.json"])

# README.md: a service keeps the inherited value for any key it does not
# set, so the effective config is the whole resolved chain. The case asserts
# that no block in tracking's chain defines the key; recompute that here.
def effective(name):
    block = services[name]
    merged = dict(effective(block["inherits"])) if "inherits" in block else {}
    merged.update(block)
    return merged

KEY = "stream_keepalive_s"
chain = effective("tracking")
if KEY in chain:
    raise SystemExit("tracking's resolved chain now defines " + KEY + "; the absent-object case is broken")

accepted = [
    "stream_keepalive_s",
    "stream keepalive",
    "keepalive interval",
]
print(json.dumps({"expected_contains_any": accepted}))
