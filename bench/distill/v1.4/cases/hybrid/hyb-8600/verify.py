# DISTILL-CANARY-8a1ad466 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://www.yunyi-express.cn/price'][0]['content']
assert files["README.md"].startswith('仓储系统的快递运费参')
assert basis.startswith('# 云驿快递运费价目表\n')
m = re.search('2026-09-01 起 \\| (\\d+) 元', basis, re.M)
val = m.group(1)
src = files['配置/运费.yaml']
old = '首重: 8'
assert src.count(old) == 1
new = src.replace(old, '首重: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/运费.yaml': new}}, ensure_ascii=False))
