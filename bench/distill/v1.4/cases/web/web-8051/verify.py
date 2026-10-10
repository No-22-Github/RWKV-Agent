# DISTILL-CANARY-6c236633 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.orbitridge.example/s2/specs'][0]["content"]
m = re.search('Claimed range: (\\d+) km', off)
assert m and m.group(1) == '55'
print(json.dumps({"expected_contains_any": ["55 km", "55km", "55 kilometres", "55 kilometers"]}, ensure_ascii=False))
