# DISTILL-CANARY-94898541 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://gantry.example/docs/v2/config'][0]["content"]
m = re.search('defaults to (\\d+)\\.', off)
assert m and m.group(1) == '7430'
print(json.dumps({"expected_contains_any": ["7430"]}, ensure_ascii=False))
