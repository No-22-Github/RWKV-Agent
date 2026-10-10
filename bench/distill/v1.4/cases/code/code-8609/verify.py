# DISTILL-CANARY-212f85e0 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['CHANGELOG.md']
assert files["README.md"].startswith('Paging hel')
assert basis.startswith('## 2026-07-1')
m = re.search('## 2026-09-20\\n- Page size raised from \\d+ to (\\d+)', basis, re.M)
val = m.group(1)
src = files['lib/paging.rb']
old = 'PAGE_SIZE = 50'
assert src.count(old) == 1
new = src.replace(old, 'PAGE_SIZE = {V}'.replace("{V}", val))
print(json.dumps({"files": {'lib/paging.rb': new}}, ensure_ascii=False))
