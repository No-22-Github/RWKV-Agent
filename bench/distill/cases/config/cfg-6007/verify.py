# DISTILL-CANARY-a7bcbff3 : distillation case
import json

case = json.load(open("case.json"))
flags = json.loads(case["files"]["flags/kiosk-flags.json"])

value = flags["receipt_email_prompt"]["rollout_pct"]

print(json.dumps({"expected_number": value}))
