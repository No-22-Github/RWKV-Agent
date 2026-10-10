# DISTILL-CANARY-6f1a9c73 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/brine-pump.json"])

# A required setting is filled in when the values block carries it, so the ones
# the controller still runs without are the required names that block leaves out.
missing = [key for key in sheet["required"] if key not in sheet["values"]]

print(json.dumps({"expected_number": len(missing)}))
