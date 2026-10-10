# DISTILL-CANARY-d3657a86 : distillation case
import json
import re

case = json.load(open("case.json"))
doc = [w for w in case["web_fixture"] if w["url"].startswith("https://quarrelmq.io/")][0]["content"]
print(json.dumps({"expected_number": int(re.search(r"defaults to (\d+)", doc).group(1))}))
