# DISTILL-CANARY-ad896a91 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "capacity" in e.get("url", ""))
m = re.search(r"最多可录入 (\d+) 组指纹", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
