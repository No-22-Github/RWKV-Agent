# DISTILL-CANARY-08b3e97a : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


tonnes = number(r"([0-9,]+) tonnes of kaolin")
trailers = number(r"over ([0-9,]+) trailers")
print(json.dumps({"expected_number": round(tonnes / trailers, 6)}))
