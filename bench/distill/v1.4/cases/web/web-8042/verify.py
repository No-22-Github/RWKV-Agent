# DISTILL-CANARY-cd2e6241 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.dgexpo-home.cn/2026'][0]["content"]
m = re.search('展期：2026 年 (\\d+ 月 \\d+) 日', off)
assert m and m.group(1) == '11 月 6'
print(json.dumps({"expected_contains_any": ["11 月 6 日", "11月6日", "11 月 6 号", "2026-11-06", "11 月 6"]}, ensure_ascii=False))
