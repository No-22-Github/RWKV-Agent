# DISTILL-CANARY-69a5f317 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://quartzly.example/pricing'][0]["content"]
files = case["files"]
f = files["docs/vendor-notes.txt"]
plan = re.match(r"Quartzly: we are on the (\w+) plan", f).group(1)
val = re.search(r"- %s: USD (\d+)\n" % plan, off).group(1)
assert val == '14'
print(json.dumps({"expected_contains_any": ["USD 14", "$14", "14 dollars", "14 USD", "US$14"]}, ensure_ascii=False))
