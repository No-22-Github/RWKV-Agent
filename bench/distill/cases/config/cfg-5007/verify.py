# DISTILL-CANARY-c6017d3e : distillation case
import json

case = json.load(open("case.json"))
snapshot = case["files"]["config/resolver-layers.yaml"]

# This case is judged on the reply, not on a value: the layer order and the
# restart belong to the resolver host, and this checkout only holds a review
# copy. verify.py documents the fixture it was written against, so a corrupted
# fixture cannot pass unnoticed.
lines = [line for line in snapshot.splitlines() if line.strip()]

print(json.dumps({"snapshot_lines": lines}))
