# DISTILL-CANARY-71f0d2e8 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def amount(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return float(m.group(1).replace(",", ""))


total = (
    amount(r"([0-9,]+\.\d{2}) in retainer drawdowns")
    + amount(r"([0-9,]+\.\d{2}) for records retrieval")
    + amount(r"([0-9,]+\.\d{2}) for court filings")
    + amount(r"an ([0-9,]+\.\d{2}) courier surcharge")
)
print(json.dumps({"expected_number": round(total, 6)}))
