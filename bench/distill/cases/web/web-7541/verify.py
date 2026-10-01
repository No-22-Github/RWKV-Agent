# DISTILL-CANARY-42ac5431 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "deprecations" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if "/v1/transfers" in l)
m = re.search(r"API version (\d+)", row)
print(json.dumps({"expected_number": float(m.group(1))}))
