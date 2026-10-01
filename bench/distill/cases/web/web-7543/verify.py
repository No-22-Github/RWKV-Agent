# DISTILL-CANARY-68f61781 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "release-notes" in e.get("url", ""))
m = re.search(r"current stable firmware is (\d+\.\d+\.\d+)", page["content"])
print(json.dumps({"expected_string": m.group(1)}))
