# DISTILL-CANARY-d95371ad : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://tessel.example/changelog'][0]["content"]
files = case["files"]
f = files["requirements.txt"]
cur = re.match(r"tessel==([\d.]+)", f).group(1)
stable = re.findall(r"## (2\.\d+\.\d+) \(\d{4}-\d\d-\d\d\)\n- Stable", off)
assert cur in stable and cur != stable[0]
val = stable[0]
assert val == '2.6.0'
print(json.dumps({"expected_contains_any": ["2.6.0"]}, ensure_ascii=False))
