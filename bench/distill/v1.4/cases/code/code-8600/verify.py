# DISTILL-CANARY-6e5af196 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['gradle.lockfile']
assert files["README.md"].startswith('移动端网络层。依赖版')
assert basis.startswith('com.squareup')
m = re.search('okhttp3:okhttp:([\\d.]+)=', basis, re.M)
val = m.group(1)
src = files['build.gradle']
old = "okhttp:4.9.3'"
assert src.count(old) == 1
new = src.replace(old, "okhttp:{V}'".replace("{V}", val))
print(json.dumps({"files": {'build.gradle': new}}, ensure_ascii=False))
