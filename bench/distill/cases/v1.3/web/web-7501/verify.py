# DISTILL-CANARY-d94b6e13 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "pricing-faq" in e.get("url", ""))
match = re.search(r"minimum stay of (\d+) weeks", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
