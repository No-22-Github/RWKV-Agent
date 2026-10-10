# DISTILL-CANARY-5e99062f : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://fjordfreight.eu/surcharges'][0]['content']
assert files["README.md"].startswith('Shipping p')
assert basis.startswith('# Fjord Frei')
m = re.search('October 2026 \\| ([\\d.]+)%', basis, re.M)
val = m.group(1)
src = files['config/shipping.env']
old = 'FUEL_SURCHARGE_PCT=13.0'
assert src.count(old) == 1
new = src.replace(old, 'FUEL_SURCHARGE_PCT={V}'.replace("{V}", val))
print(json.dumps({"files": {'config/shipping.env': new}}, ensure_ascii=False))
