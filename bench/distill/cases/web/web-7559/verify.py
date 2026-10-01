# DISTILL-CANARY-bd2d8906 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.chengquan.example" in e.get("url", ""))
match = re.search(r"RO 膜滤芯建议每 (\d+) 个月", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
