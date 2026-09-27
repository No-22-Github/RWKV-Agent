# DISTILL-CANARY-61d98b3e : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


booking = number(r"booked at ([0-9,]+)")
percent = number(r"pays ([0-9.]+) percent")
print(json.dumps({"expected_number": round(booking * percent / 100, 6)}))
