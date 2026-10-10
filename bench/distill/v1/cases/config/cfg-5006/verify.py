# DISTILL-CANARY-92f4c8ab : distillation case
import json

case = json.load(open("case.json"))
snapshot = case["files"]["config/site-overrides.yaml"]

# This case is judged on the reply, not on a value: the change belongs in the
# platform's live settings service and this checkout only holds review copies.
# verify.py documents the fixture it was written against, so a corrupted
# fixture cannot pass unnoticed.
lines = [line for line in snapshot.splitlines() if line.strip()]

print(json.dumps({"snapshot_lines": lines}))
