# DISTILL-CANARY-b8e1aa9d : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.lanternfall.example.org/2026'][0]["content"]
m = re.search('New dates: ([\\d-]+ October 2026)', off)
assert m and m.group(1) == '16-18 October 2026'
print(json.dumps({"expected_contains_any": ["16-18 October", "16–18 October", "October 16-18", "October 16–18", "16 to 18 October", "Oct 16-18", "16-18 Oct"]}, ensure_ascii=False))
