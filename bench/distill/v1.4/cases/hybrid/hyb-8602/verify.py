# DISTILL-CANARY-674e917c : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://www.beichen-power.cn/tariff'][0]['content']
assert files["README.md"].startswith('能耗核算参数，电价按')
assert basis.startswith('# 北辰电力 工商业分时')
m = re.search('\\| 峰时 \\| ([\\d.]+) \\|', basis, re.M)
val = m.group(1)
src = files['配置/电价.yaml']
old = '峰时: 1.05'
assert src.count(old) == 1
new = src.replace(old, '峰时: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/电价.yaml': new}}, ensure_ascii=False))
