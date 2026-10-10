# DISTILL-CANARY-aaa88f4b : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://quillpost.io/pricing'][0]['content']
assert files["README.md"].startswith('Billing es')
assert basis.startswith('# Quillpost ')
m = re.search('price per SMS segment \\(EU\\): \\$([\\d.]*\\d)', basis, re.M)
val = m.group(1)
src = files['config/billing.toml']
old = 'eu_per_segment = 0.0065'
assert src.count(old) == 1
new = src.replace(old, 'eu_per_segment = {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/billing.toml': new}}, ensure_ascii=False))
