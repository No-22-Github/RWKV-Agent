# DISTILL-CANARY-b063edc8 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "convert-changelog" in e.get("url", ""))
m = re.search(r"Current stable: (\d+\.\d+\.\d+)", page["content"])
print(json.dumps({"expected_string": m.group(1)}))
