# DISTILL-CANARY-cfa66765 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.xunda-express.cn/price/surcharge'][0]["content"]
m = re.search('单件超过 (\\d+) 公斤', off)
assert m and m.group(1) == '25'
print(json.dumps({"expected_contains_any": ["25 公斤", "25公斤", "25 kg", "25kg", "25 千克"]}, ensure_ascii=False))
