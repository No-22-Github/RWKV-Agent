# DISTILL-CANARY-d4712f0c : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


usd = number(r"deposit is ([0-9,]+) US dollars")
rate = number(r"([0-9.]+) dollars per pound")
print(json.dumps({"expected_number": round(usd / rate, 6)}))
