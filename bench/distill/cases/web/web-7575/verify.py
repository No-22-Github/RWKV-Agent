# DISTILL-CANARY-9ab0f31f : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.qingsuibook.example" in e.get("url", ""))
match = re.search(r"于 (\d{4}-\d{2}-\d{2}) 停止服务", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
