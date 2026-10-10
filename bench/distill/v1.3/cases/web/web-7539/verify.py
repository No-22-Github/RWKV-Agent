# DISTILL-CANARY-29149a98 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "changelog" in e.get("url", ""))
m = re.search(r"当前稳定版：(\d+\.\d+\.\d+)", page["content"])
print(json.dumps({"expected_string": m.group(1)}))
