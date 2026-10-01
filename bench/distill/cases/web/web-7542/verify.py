# DISTILL-CANARY-9e83ef94 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "pitches" in e.get("url", ""))
m = re.search(r"one tent up to (\d+) occupants", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
