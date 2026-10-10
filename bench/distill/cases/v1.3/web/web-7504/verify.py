# DISTILL-CANARY-f06b9342 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "deprecations" in e.get("url", ""))
match = re.search(r"removed in API version (\d+)", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
