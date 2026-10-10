# DISTILL-CANARY-a8c3e109 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.ludao-ferry.cn/fares'][0]["content"]
m = re.search('成人单程 (\\d+) 元', off)
assert m and m.group(1) == '22'
print(json.dumps({"expected_contains_any": ["22 元", "22元", "二十二元"]}, ensure_ascii=False))
