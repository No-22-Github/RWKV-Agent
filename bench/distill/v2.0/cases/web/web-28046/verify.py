# DISTILL-CANARY-12faf95f : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://gjj.binjiang.gov.cn/notice/2026-base'][0]["content"]
m = re.search('上限 (\\d+) 元', off)
assert m and m.group(1) == '31200'
print(json.dumps({"expected_contains_any": ["31200", "31,200", "3.12 万", "3.12万"]}, ensure_ascii=False))
