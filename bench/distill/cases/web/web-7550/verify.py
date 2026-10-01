# DISTILL-CANARY-6133e8bc : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "temp-password" in e.get("url", ""))
m = re.search(r"最长有效期为 (\d+) 小时", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
