# DISTILL-CANARY-0af1b5dc : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.yungang-lib.cn/rules/borrow'][0]["content"]
m = re.search('借期 (\\d+) 天，可续借一次', off)
assert m and m.group(1) == '45'
print(json.dumps({"expected_contains_any": ["45 天", "45天", "四十五天"]}, ensure_ascii=False))
