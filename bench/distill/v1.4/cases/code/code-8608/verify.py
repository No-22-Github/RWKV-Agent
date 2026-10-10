# DISTILL-CANARY-739ee8c3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['Gemfile.lock']
assert files["README.md"].startswith('Rails app.')
assert basis.startswith('GEM\n  specs:')
m = re.search('\\n    rails \\(([\\d.]+)\\)', basis, re.M)
val = m.group(1)
src = files['Gemfile']
old = "gem 'rails', '7.0.8'"
assert src.count(old) == 1
new = src.replace(old, "gem 'rails', '{V}'".replace("{V}", val))
print(json.dumps({"files": {'Gemfile': new}}, ensure_ascii=False))
