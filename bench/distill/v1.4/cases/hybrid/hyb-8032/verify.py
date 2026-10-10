# DISTILL-CANARY-f8a86c23 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://alder.example/hub/pricing'][0]["content"]
files = case["files"]
f = files["shop/stock-note.txt"]
model = re.match(r"Stocked model: Alder (Hub \w+)", f).group(1)
val = re.search(r"\| %s \| EUR (\d+) \|" % model, off).group(1)
assert val == '89'
print(json.dumps({"expected_contains_any": ["EUR 89", "€89", "89 euro", "89 EUR", "89 euros"]}, ensure_ascii=False))
