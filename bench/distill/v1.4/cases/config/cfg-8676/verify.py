# DISTILL-CANARY-d7f372b8 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['vendor/modules.txt']
assert files["README.md"].startswith('Billing se')
assert basis.startswith('# github.com')
m = re.search('# github.com/jackc/pgx/v5 (v[\\d.]+)', basis, re.M)
val = m.group(1)
src = files['go.mod']
old = 'github.com/jackc/pgx/v5 v5.4.3'
assert src.count(old) == 1
new = src.replace(old, 'github.com/jackc/pgx/v5 {V}'.replace("{V}", val))
print(json.dumps({"files": {'go.mod': new}}, ensure_ascii=False))
