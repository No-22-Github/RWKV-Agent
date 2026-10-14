# DISTILL-CANARY-af89bd2f : distillation case
import json
import re

VALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"[IVXLCDM]{2,}", prompt).group(0)
total = 0
for i, ch in enumerate(token):
    v = VALS[ch]
    if i + 1 < len(token) and VALS[token[i + 1]] > v:
        total -= v
    else:
        total += v
print(json.dumps({"expected_number": total}))
