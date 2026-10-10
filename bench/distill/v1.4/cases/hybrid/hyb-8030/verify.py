# DISTILL-CANARY-31523d5a : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.fennmoorrail.example/railcards'][0]["content"]
files = case["files"]
f = files["travel/notes.txt"]
card = re.match(r"Card we're considering: (\w+) Railcard", f).group(1)
val = re.search(r"- %s Railcard: age (\d+) or over" % card, off).group(1)
assert val == '60'
print(json.dumps({"expected_contains_any": ["60 or over", "age 60", "aged 60", "60 and over", "60 or older", "60 years", "60+"]}, ensure_ascii=False))
