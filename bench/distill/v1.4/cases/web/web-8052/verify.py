# DISTILL-CANARY-abd78181 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.marlowcounty.example.gov/parking/permits'][0]["content"]
m = re.search('annual permit USD (\\d+)', off)
assert m and m.group(1) == '96'
print(json.dumps({"expected_contains_any": ["USD 96", "$96", "96 dollars", "96 USD", "US$96"]}, ensure_ascii=False))
