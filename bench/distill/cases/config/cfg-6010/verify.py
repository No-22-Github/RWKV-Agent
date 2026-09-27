# DISTILL-CANARY-d0357d5e : distillation case
import json

case = json.load(open("case.json"))
services = json.loads(case["files"]["config/services.json"])

# README.md: a service keeps the inherited value for any key it does not
# set, so the effective config is the whole resolved chain.
def effective(name):
    block = services[name]
    merged = dict(effective(block["inherits"])) if "inherits" in block else {}
    merged.update(block)
    return merged

KEY = "stream_keepalive_s"
chain = effective("tracking")
value = "UNKNOWN"
if KEY in chain:
    value = chain[KEY]

print(json.dumps({"expected_string": value}))
