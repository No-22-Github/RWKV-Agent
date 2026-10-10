# DISTILL-CANARY-4ab936e9 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://ember-runtime.dev/releases'][0]['content']
assert files["README.md"].startswith('Dev enviro')
assert basis.startswith('# Ember runt')
m = re.search('\\| (\\d+) \\| Active LTS \\|', basis, re.M)
val = m.group(1)
src = files['.tool-versions']
old = 'ember 22'
assert src.count(old) == 1
new = src.replace(old, 'ember {V}'.replace("{V}", val))
print(json.dumps({"files": {'.tool-versions': new}}, ensure_ascii=False))
