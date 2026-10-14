# DISTILL-CANARY-03289383 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.yunti-arena.cn/about/capacity'][0]["content"]
m = re.search('最大容量 (\\d+) 人', off)
assert m and m.group(1) == '21500'
print(json.dumps({"expected_contains_any": ["21500", "21,500", "2.15 万", "2.15万"]}, ensure_ascii=False))
