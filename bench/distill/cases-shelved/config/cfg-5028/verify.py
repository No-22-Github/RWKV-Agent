# DISTILL-CANARY-3a5d7f92 : distillation case
import json

case = json.load(open("case.json"))
sheets = {
    "config/monitor-base.yaml": case["files"]["config/monitor-base.yaml"],
    "config/monitor-change.yaml": case["files"]["config/monitor-change.yaml"],
}

# This case is judged on the reply, not on a value: the load is made on the
# monitor's own console, and this folder holds the two partial sheets instead.
# The folded set is still computed here, so a corrupted fixture cannot pass
# unnoticed.
folded = {}
for name in ("config/monitor-base.yaml", "config/monitor-change.yaml"):
    for line in sheets[name].splitlines():
        key, _, raw = line.partition(":")
        folded[key.strip()] = raw.strip()

print(json.dumps({"snapshot_folded_set": folded}))
