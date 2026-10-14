# DISTILL-CANARY-0001382f : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://ferrule.example/docs/install'][0]["content"]
m = re.search('requires Python ([\\d.]+) or newer', off)
assert m and m.group(1) == '3.10'
print(json.dumps({"expected_contains_any": ["3.10", "Python 3.10"]}, ensure_ascii=False))
