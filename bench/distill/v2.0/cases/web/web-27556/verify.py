# DISTILL-CANARY-05246b81 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "service.ashmillcycles.example" in e.get("url", ""))
match = re.search(r"headset cap bolts torque to (\d+) Nm", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
