# DISTILL-CANARY-96e5b183 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


eur = number(r"credit note is ([0-9,]+) euros")
rate = number(r"([0-9.]+) Canadian dollars per euro")
print(json.dumps({"expected_number": round(eur * rate, 6)}))
