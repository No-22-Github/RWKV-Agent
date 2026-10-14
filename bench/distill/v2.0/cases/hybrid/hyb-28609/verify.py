# DISTILL-CANARY-57430f49 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://lumencerts.org/policy/validity'][0]['content']
assert files["README.md"].startswith('Certificat')
assert basis.startswith('# Lumen Cert')
m = re.search('on or after [\\d-]+ are valid for at most (\\d+) days', basis, re.M)
val = m.group(1)
src = files['config/renewal.yaml']
old = 'validity_days: 200'
assert src.count(old) == 1
new = src.replace(old, 'validity_days: {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/renewal.yaml': new}}, ensure_ascii=False))
