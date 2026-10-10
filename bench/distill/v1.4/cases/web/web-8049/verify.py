# DISTILL-CANARY-ec4077a5 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.corvid.air/help/baggage'][0]["content"]
m = re.search('up to (\\d+) kg \\(55', off)
assert m and m.group(1) == '10'
print(json.dumps({"expected_contains_any": ["10 kg", "10kg", "10 kilograms", "10 kilos", "ten kilograms"]}, ensure_ascii=False))
