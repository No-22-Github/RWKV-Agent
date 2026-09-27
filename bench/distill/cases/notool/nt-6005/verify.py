# DISTILL-CANARY-5a9c07d4 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


volume = number(r"holding ([0-9,]+) litres")
rate = number(r"moves ([0-9,]+) litres per minute")
print(json.dumps({"expected_number": round(volume / rate, 6)}))
