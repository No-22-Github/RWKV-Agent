# DISTILL-CANARY-4af3d339 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://www.qinglanshan.cn/ticket'][0]['content']
assert files["README.md"].startswith('订票系统票价参数。\n')
assert basis.startswith('# 青岚山景区门票公告\n')
m = re.search('旺季（4-10 月）成人票价调整为 (\\d+) 元', basis, re.M)
val = m.group(1)
src = files['配置/票价.ini']
old = '旺季成人 = 85'
assert src.count(old) == 1
new = src.replace(old, '旺季成人 = {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/票价.ini': new}}, ensure_ascii=False))
