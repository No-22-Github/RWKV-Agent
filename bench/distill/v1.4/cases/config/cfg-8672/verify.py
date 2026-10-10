# DISTILL-CANARY-5af9ddee : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['Cargo.lock']
assert files["README.md"].startswith('数据接入服务。\n')
assert basis.startswith('[[package]]\n')
m = re.search('name = "serde"\\nversion = "([^"]+)"', basis, re.M)
val = m.group(1)
src = files['Cargo.toml']
old = 'serde = "1.0.190"'
assert src.count(old) == 1
new = src.replace(old, 'serde = "{V}"'.replace("{V}", val))
print(json.dumps({"files": {'Cargo.toml': new}}, ensure_ascii=False))
