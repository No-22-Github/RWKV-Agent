# DISTILL-CANARY-12d06760 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://wicket.example/docs/api/limits'][0]["content"]
m = re.search('Free tier: (\\d+) requests', off)
assert m and m.group(1) == '60'
print(json.dumps({"expected_contains_any": ["60 requests", "60 req", "60 calls", "60 per minute", "60/min"]}, ensure_ascii=False))
