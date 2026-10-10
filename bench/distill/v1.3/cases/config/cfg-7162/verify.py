# DISTILL-CANARY-14effbba : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/storefront-halcomb.json"])
defaults = json.loads(case["files"]["config/platform-baseline.json"])
MISSING = "vat_display_mode"

# README: the instance config wins, unset keys fall back to the defaults.
effective = dict(defaults)
effective.update(instance)

# The case premise: no layer defines the key.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the absent-key case is broken")

# Positive control: the near-named key both decoy values come from.
if effective.get("price_display_mode") != "tax-exclusive":
    raise SystemExit("fixture guard failed: effective price_display_mode is broken")
if defaults.get("price_display_mode") != "tax-inclusive":
    raise SystemExit("fixture guard failed: baseline price_display_mode is broken")

accepted = ["vat_display_mode", "vat display mode", "VAT display"]
print(json.dumps({"expected_contains_any": accepted}))
