# DISTILL-CANARY-68978e0a : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = [w for w in case['web_fixture'] if w['url'] == 'https://harbormail.example/rates'][0]['content']
assert files["README.md"].startswith('Mailroom s')
assert basis.startswith('# Harbor Mai')
m = re.search('Standard letter \\(up to 50 g\\): ([\\d.]*\\d) EUR', basis, re.M)
val = m.group(1)
src = files['config/postage.ini']
old = 'standard_letter = 1.25'
assert src.count(old) == 1
new = src.replace(old, 'standard_letter = {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/postage.ini': new}}, ensure_ascii=False))
