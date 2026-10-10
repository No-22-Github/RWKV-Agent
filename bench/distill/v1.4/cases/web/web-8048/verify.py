# DISTILL-CANARY-b3e70578 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.kestrelpoint.org/visit/tours'][0]["content"]
m = re.search('Sundays is at (\\d+:\\d+)', off)
assert m and m.group(1) == '15:00'
print(json.dumps({"expected_contains_any": ["15:00", "3 pm", "3pm", "3 p.m.", "3:00 pm", "3:00 PM", "3 PM"]}, ensure_ascii=False))
