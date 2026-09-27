# DISTILL-CANARY-382e639a : distillation case
import json

case = json.load(open("case.json"))
services = json.loads(case["files"]["config/services.json"])

# README.md: a service block applies its own keys on top of the block named
# in "inherits", and chains can run more than one step deep.
def effective(name):
    block = services[name]
    merged = dict(effective(block["inherits"])) if "inherits" in block else {}
    merged.update(block)
    return merged

value = effective("tracking")["request_timeout_s"]

print(json.dumps({"expected_number": value}))
