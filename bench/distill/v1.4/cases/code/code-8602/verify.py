# DISTILL-CANARY-0016ea27 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['yarn.lock']
assert files["README.md"].startswith('前端构建脚本。\n')
assert basis.startswith('"@babel/core')
m = re.search('"@babel/core@[^"]+":\\n  version "([\\d.]+)"', basis, re.M)
val = m.group(1)
src = files['scripts/versions.js']
old = "babelCore: '7.22.5'"
assert src.count(old) == 1
new = src.replace(old, "babelCore: '{V}'".replace("{V}", val))
print(json.dumps({"files": {'scripts/versions.js': new}}, ensure_ascii=False))
