# DISTILL-CANARY-e1c9bafa : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['registry/sites.csv']
assert files["README.md"].startswith('Clock conf')
assert basis.startswith('site,city,ut')
m = re.search('^plant-b,[^,]+,([+-][\\d:]+)$', basis, re.M)
val = m.group(1)
src = files['config/clock.ini']
old = '[plant-b]\nutc_offset = +01:00'
assert src.count(old) == 1
new = src.replace(old, '[plant-b]\nutc_offset = {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/clock.ini': new}}, ensure_ascii=False))
