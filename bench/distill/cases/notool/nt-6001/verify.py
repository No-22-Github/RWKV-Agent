# DISTILL-CANARY-b04a1c93 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def amount(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


total = (
    amount(r"([0-9,]+\.\d{2}) for concept boards")
    + amount(r"([0-9,]+\.\d{2}) for site visits")
    + amount(r"([0-9,]+\.\d{2}) for the furniture schedule")
    + amount(r"a ([0-9,]+\.\d{2}) late fee")
)
print(json.dumps({"expected_number": round(total, 6)}))
