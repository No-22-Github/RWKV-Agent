# DISTILL-CANARY-c84a1e73 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/chiller.json"])

# README.md: the controller needs a value for every entry in required_settings.
unset = [key for key in sheet["required_settings"] if key not in sheet["configured"]]
print(json.dumps({"expected_number": len(unset)}))
