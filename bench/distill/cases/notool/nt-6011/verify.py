# DISTILL-CANARY-c0574ea2 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


invoice = number(r"invoiced at ([0-9,]+)")
percent = number(r"pays ([0-9.]+) percent")
print(json.dumps({"expected_number": round(invoice * percent / 100, 6)}))
