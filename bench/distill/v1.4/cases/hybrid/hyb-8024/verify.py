# DISTILL-CANARY-6b107dc9 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.xingqiao-expo.cn/halls'][0]["content"]
files = case["files"]
f = files["合同/场地租赁.txt"]
h = re.match(r"场地：星桥会展中心 (\w) 厅", f).group(1)
val = re.search(r"\| %s 厅 \| \d+ ㎡ \| (\d+) 人" % h, off).group(1)
assert val == '520'
print(json.dumps({"expected_contains_any": ["520 人", "520人", "520 个座位", "520 座"]}, ensure_ascii=False))
