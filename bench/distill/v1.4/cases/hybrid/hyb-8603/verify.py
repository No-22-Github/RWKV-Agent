# DISTILL-CANARY-9bbb3c46 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://shbj.songjiang-gov.cn/base'][0]['content']
assert files["README.md"].startswith('薪资系统的社保参数。')
assert basis.startswith('# 松江市 2026 年')
m = re.search('缴费基数上限：(\\d+) 元/月', basis, re.M)
val = m.group(1)
src = files['配置/社保.yaml']
old = '基数上限: 23100'
assert src.count(old) == 1
new = src.replace(old, '基数上限: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/社保.yaml': new}}, ensure_ascii=False))
