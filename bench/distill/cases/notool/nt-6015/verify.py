# DISTILL-CANARY-1a6e84f0 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return int(m.group(1).replace(",", ""))


day_one = number(r"([0-9]+) badges were scanned on day one")
day_two = number(r"and ([0-9]+) on day two")
both = number(r"and ([0-9]+) of the day-one visitors")
print(json.dumps({"expected_number": day_one + day_two - both}))
