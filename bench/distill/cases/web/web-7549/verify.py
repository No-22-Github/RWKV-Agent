# DISTILL-CANARY-3c048d43 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "guard-notes" in e.get("url", ""))
m = re.search(r"Guard (\d+\.\d+\.\d+) is the current stable", page["content"])
print(json.dumps({"expected_string": m.group(1)}))
