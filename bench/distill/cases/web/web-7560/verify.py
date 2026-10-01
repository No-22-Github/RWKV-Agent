# DISTILL-CANARY-82b68f7e : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.zhutaostudio.example/baoming" in e.get("url", ""))
match = re.search(r"每场最多 (\d+) 人", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
