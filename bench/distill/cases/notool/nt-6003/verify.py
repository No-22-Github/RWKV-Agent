# DISTILL-CANARY-3c95a0b7 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def amount(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


total = (
    amount(r"([0-9,]+\.\d{2}) for glazed planters")
    + amount(r"([0-9,]+\.\d{2}) for packing crates")
    + amount(r"([0-9,]+\.\d{2}) for the dinnerware order")
    + amount(r"a ([0-9,]+\.\d{2}) restocking fee")
)
print(json.dumps({"expected_number": round(total, 6)}))
