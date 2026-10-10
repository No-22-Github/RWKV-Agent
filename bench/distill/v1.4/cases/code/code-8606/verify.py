# DISTILL-CANARY-a9d4576d : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['reports/bom.txt']
assert files["README.md"].startswith('Maven buil')
assert basis.startswith('jackson-data')
m = re.search('logback-classic ([\\d.]+)', basis, re.M)
val = m.group(1)
src = files['pom.xml']
old = '<logback.version>1.4.14</logback.version>'
assert src.count(old) == 1
new = src.replace(old, '<logback.version>{V}</logback.version>'.replace("{V}", val))
print(json.dumps({"files": {'pom.xml': new}}, ensure_ascii=False))
