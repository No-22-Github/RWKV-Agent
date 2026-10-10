# DISTILL-CANARY-d2f60a8c : distillation case
import json

case = json.load(open("case.json"))
pack = case["files"]["config/lock-commissioning.yaml"]

# This case is judged on the reply, not on a value: the interval the controller
# is running with can only be read at the cabin panel, and this pack holds the
# figures it was commissioned with instead. verify.py documents the fixture it
# was written against, so a corrupted fixture cannot pass unnoticed.
intervals = {}
for line in pack.splitlines():
    key, _, raw = line.partition(":")
    if key.strip().endswith("_s"):
        intervals[key.strip()] = int(raw.strip())

print(json.dumps({"snapshot_intervals": intervals}))
