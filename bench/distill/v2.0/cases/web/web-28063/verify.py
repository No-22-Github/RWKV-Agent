# DISTILL-CANARY-971e8858 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.hollingorge.example.org/visit/fees'][0]["content"]
m = re.search('adult entry GBP ([\\d.]+)', off)
assert m and m.group(1) == '7.50'
print(json.dumps({"expected_contains_any": ["7.50", "7.5 pounds", "GBP 7.5 "]}, ensure_ascii=False))
