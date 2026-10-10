# DISTILL-CANARY-3107d628 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.brindle.example/support/q1-warranty'][0]["content"]
m = re.search('carry a (\\d)-year manufacturer warranty', off)
assert m and m.group(1) == '3'
print(json.dumps({"expected_contains_any": ["3-year", "3 year", "three-year", "three year", "3 years", "three years", "Three-year", "Three year", "Three years"]}, ensure_ascii=False))
