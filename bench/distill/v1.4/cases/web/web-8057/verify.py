# DISTILL-CANARY-554ae24c : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.northmoorrail.example/passes/youth'][0]["content"]
m = re.search('aged 16 to (\\d+)', off)
assert m and m.group(1) == '27'
print(json.dumps({"expected_contains_any": ["27 years", "age 27", "aged 27", "16 to 27", "16-27", "16–27", "up to 27", "27 inclusive", "27 or younger", "27 and under", "27th birthday"]}, ensure_ascii=False))
