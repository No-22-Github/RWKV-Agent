# DISTILL-CANARY-bbb503ca : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://sorrel-db.example/docs/3.x/settings'][0]["content"]
m = re.search('default (\\d+)\\. Raised', off)
assert m and m.group(1) == '400'
print(json.dumps({"expected_contains_any": ["defaults to 400", "default of 400", "is 400", "400 connections", "400 by default", "default 400", "= 400", "to 400"]}, ensure_ascii=False))
