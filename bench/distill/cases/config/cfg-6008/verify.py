# DISTILL-CANARY-3a5c5233 : distillation case
import json

case = json.load(open("case.json"))
flags = json.loads(case["files"]["flags/kiosk-flags.json"])

KEY = "gift_receipt_printing"

# README.md: a flag that is not on the sheet is not part of the kiosk build, and
# the sheet is the only place flags are set. The case asserts the sheet carries
# no gift_receipt_printing entry; recompute that here.
if KEY in flags:
    raise SystemExit("flag sheet now lists " + KEY + "; the absent-object case is broken")

accepted = [
    "gift_receipt_printing",
    "gift receipt",
    "gift-receipt",
]
print(json.dumps({"expected_contains_any": accepted}))
