# DISTILL-CANARY-18d98ce3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://stratus-cloud.com/object-storage/pricing'][0]['content']
assert files["README.md"].startswith('FinOps cos')
assert basis.startswith('# Stratus Ob')
m = re.search('Standard tier: \\$([\\d.]+) per GB-month', basis, re.M)
val = m.group(1)
src = files['costmodel/rates.yaml']
old = 'standard_gb_month: 0.023'
assert src.count(old) == 1
new = src.replace(old, 'standard_gb_month: {V}'.replace("{V}", val))
print(json.dumps({"files": {'costmodel/rates.yaml': new}}, ensure_ascii=False))
