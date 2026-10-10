# DISTILL-CANARY-d08b6037 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.lumo-mobile.cn/x5/specs'][0]["content"]
m = re.search('电池：(\\d+) mAh', off)
assert m and m.group(1) == '5200'
print(json.dumps({"expected_contains_any": ["5200 mAh", "5200mAh", "5200 毫安", "5200毫安", "5200 mah"]}, ensure_ascii=False))
