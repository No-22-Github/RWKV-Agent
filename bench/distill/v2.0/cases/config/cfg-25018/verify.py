# DISTILL-CANARY-b7f29d4a : distillation case
import json

case = json.load(open("case.json"))

# This case is judged on the reply, not on a value: the parameter store runs on
# the farm controller host and is written through its own console, while this
# checkout holds the farm team's working copies. verify.py documents the fixture
# it was written against, so a corrupted fixture cannot pass unnoticed.
blocks = {}
for path, text in case["files"].items():
    if not path.startswith("params/"):
        continue
    keys = [line.partition(":")[0].strip() for line in text.splitlines() if ":" in line]
    blocks[path] = sorted(keys)

print(json.dumps({"working_copy_keys": blocks}))
