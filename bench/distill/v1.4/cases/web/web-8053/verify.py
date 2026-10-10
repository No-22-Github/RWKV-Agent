# DISTILL-CANARY-e8fa89ea : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.ashgrove.example.edu/admissions/dates'][0]["content"]
m = re.search('Main application deadline: (\\d+ January 2027)', off)
assert m and m.group(1) == '15 January 2027'
print(json.dumps({"expected_contains_any": ["15 January 2027", "January 15, 2027", "2027-01-15", "15 Jan 2027", "Jan 15, 2027", "15 January"]}, ensure_ascii=False))
