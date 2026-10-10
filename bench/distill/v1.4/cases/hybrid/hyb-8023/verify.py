# DISTILL-CANARY-641e3285 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.hanhai-air.cn/baggage'][0]["content"]
files = case["files"]
f = files["出差/计划.txt"]
cab = re.match(r"舱位：(\S+)", f).group(1)
val = re.search(r"\| %s \| (\d+) 公斤" % cab, off).group(1)
assert val == '40'
print(json.dumps({"expected_contains_any": ["40 公斤", "40公斤", "40 kg", "40kg", "40 千克"]}, ensure_ascii=False))
