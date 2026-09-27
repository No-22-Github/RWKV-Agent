# DISTILL-CANARY-8b3f16d9 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


value = number(r"worth ([0-9,]+)")
percent = number(r"rate is ([0-9.]+) percent")
print(json.dumps({"expected_number": round(value * percent / 100, 6)}))
