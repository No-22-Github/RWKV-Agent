# DISTILL-CANARY-7ac39e54 : distillation case
import json

case = json.load(open("case.json"))
spec = json.loads(case["files"]["config/pressline.json"])

required = spec["required_settings"]
configured = spec["configured"]
unset = [key for key in required if key not in configured]

print(json.dumps({"expected_number": len(unset)}))
