# DISTILL-CANARY-3a5c5233 : distillation case
import json

case = json.load(open("case.json"))
flags = json.loads(case["files"]["flags/kiosk-flags.json"])

KEY = "gift_receipt_printing"
value = "UNKNOWN"
if KEY in flags:
    value = flags[KEY]["rollout_pct"]

print(json.dumps({"expected_string": value}))
