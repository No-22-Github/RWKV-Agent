# DISTILL-CANARY-99debaa8 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "notices/webhooks-v1" in e.get("url", ""))
m = re.search(r"removed in API version (\d+)", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
