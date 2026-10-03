# DISTILL-CANARY-b6ebdebf : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("区域货运报价服务")
lines = case["files"]["billing/tariff.py"].splitlines()
print(json.dumps({"expected_number": [i + 1 for i, l in enumerate(lines) if l.startswith("def load_tariff_table(")][0]}))
