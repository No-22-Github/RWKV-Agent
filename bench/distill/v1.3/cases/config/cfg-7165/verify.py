# DISTILL-CANARY-d798dc6b : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/printshop.json"])
defaults = json.loads(case["files"]["config/shop-defaults.json"])
KNOWN = "bind_edge_default"
MISSING = "cover_lamination_type"

# README: instance config wins, unset keys fall back to the defaults.
effective = dict(defaults)
effective.update(instance)

# Half the answer is verifiable and must resolve to the pinned value...
if effective.get(KNOWN) != "left":
    raise SystemExit("fixture guard failed: bind_edge_default is broken")
# ...and the other half must be undefined in every layer.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

# Positive control: the near-named key the decoy value comes from.
if defaults.get("paper_lamination_type") != "MATTE-350G":
    raise SystemExit("fixture guard failed: paper lamination decoy is broken")

accepted = ["cover_lamination_type", "覆膜"]
print(json.dumps({"expected_contains_any": accepted}))
