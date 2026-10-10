# DISTILL-CANARY-2f7ac450 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


chf = number(r"order is ([0-9,]+) Swiss francs")
rate = number(r"([0-9.]+) dollars per franc")
print(json.dumps({"expected_number": round(chf * rate, 6)}))
