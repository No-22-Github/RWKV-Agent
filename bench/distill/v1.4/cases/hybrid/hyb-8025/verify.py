# DISTILL-CANARY-a7662f34 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.anlan-gas.cn/price/residential'][0]["content"]
files = case["files"]
f = files["家庭/账单备忘.txt"]
tier = re.match(r"燃气：.*属于(第.档)", f).group(1)
val = re.search(r"- %s（[^）]*）：([\d.]+) 元" % tier, off).group(1)
assert val == '3.78'
print(json.dumps({"expected_contains_any": ["3.78 元", "3.78元", "3.78 块"]}, ensure_ascii=False))
