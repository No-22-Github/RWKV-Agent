# DISTILL-CANARY-7f632b72 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.haiyan-air.cn/service/baggage'][0]["content"]
m = re.search('国内航线 (\\d+) 公斤', off)
assert m and m.group(1) == '20'
print(json.dumps({"expected_contains_any": ["20 公斤", "20公斤", "20 kg", "20kg", "20 千克"]}, ensure_ascii=False))
