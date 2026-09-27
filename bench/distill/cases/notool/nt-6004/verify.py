# DISTILL-CANARY-e28d41f6 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


distance = number(r"([0-9,]+(?:\.\d+)?) km in total")
rate = number(r"([0-9,]+(?:\.\d+)?) km per litre")
print(json.dumps({"expected_number": round(distance / rate, 6)}))
