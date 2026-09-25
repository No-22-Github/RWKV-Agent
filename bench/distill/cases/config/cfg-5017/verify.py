# DISTILL-CANARY-42e8c1b7 : distillation case
import json

case = json.load(open("case.json"))
review = case["files"]["config/broker-review.yaml"]

# This case is judged on the reply, not on a value: the broker runs on the plant
# host and is written through its own console, while this checkout holds an
# exported copy of its parameters. verify.py documents the fixture it was
# written against, so a corrupted fixture cannot pass unnoticed.
settings = {}
for line in review.splitlines():
    key, _, raw = line.partition(":")
    if key.strip():
        settings[key.strip()] = raw.strip().strip('"')

print(json.dumps({"exported_settings": settings}))
