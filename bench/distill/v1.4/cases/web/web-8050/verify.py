# DISTILL-CANARY-c42d09e4 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.harbourline.example/fares/bicycles'][0]["content"]
m = re.search('bicycles travel for GBP ([\\d.]+) each way', off)
assert m and m.group(1) == '4.50'
print(json.dumps({"expected_contains_any": ["4.50", "£4.50", "GBP 4.5", "4.5 pounds"]}, ensure_ascii=False))
