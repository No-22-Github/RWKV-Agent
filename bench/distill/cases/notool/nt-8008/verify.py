# DISTILL-CANARY-35abc10b : distillation case
import json
from datetime import date

case = json.load(open("case.json"))
assert "12800 元" in case["turns"][0]["prompt"]
d = (date(2026, 12, 31) - date(2026, 9, 17)).days + 1
fee = round(12800 * d / 365, 2)
print(json.dumps({"expected_contains_any": sorted({"%.2f" % fee, "{:,.2f}".format(fee)})}))
