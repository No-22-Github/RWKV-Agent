# DISTILL-CANARY-f6637c96 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(\d+):(\d+) (AM|PM)", prompt)
hour, minute = int(m.group(1)), int(m.group(2))
if m.group(3) == "PM" and hour < 12:
    hour += 12
if m.group(3) == "AM" and hour == 12:
    hour = 0
assert "%d:%02d" % (hour, minute) == "19:25"
print(json.dumps({"expected_contains_any": ["19:25", "19:25 hours"]}))
