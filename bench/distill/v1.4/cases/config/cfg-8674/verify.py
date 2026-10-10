# DISTILL-CANARY-c2ecbe31 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['contracts/order-form-2026Q3.txt']
assert files["README.md"].startswith('Rate limit')
assert basis.startswith('Quote Q-118 ')
m = re.search('signed 2026-08-14\\): Pro tier (\\d+) requests/min', basis, re.M)
val = m.group(1)
src = files['config/ratelimit.yaml']
old = 'requests_per_min: 600'
assert src.count(old) == 1
new = src.replace(old, 'requests_per_min: {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/ratelimit.yaml': new}}, ensure_ascii=False))
