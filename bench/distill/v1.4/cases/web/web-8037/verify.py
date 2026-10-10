# DISTILL-CANARY-7d99c328 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.wangchao-museum.cn/visit'][0]["content"]
m = re.search('周二至周日 9:00—(\\d+:\\d+)', off)
assert m and m.group(1) == '17:30'
print(json.dumps({"expected_contains_any": ["17:30", "17 点半", "下午 5 点半", "下午5点半", "五点半"]}, ensure_ascii=False))
