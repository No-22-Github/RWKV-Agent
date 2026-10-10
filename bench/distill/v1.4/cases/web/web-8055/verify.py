# DISTILL-CANARY-d954aa44 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.plovernotes.example/pricing'][0]["content"]
m = re.search('Pro: USD (\\d+) per month', off)
assert m and m.group(1) == '6'
print(json.dumps({"expected_contains_any": ["USD 6", "$6 ", "$6/", "$6.", "6 dollars", "6 USD", "US$6"]}, ensure_ascii=False))
