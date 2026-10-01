# DISTILL-CANARY-41f9c8ab : distillation case
import json
import re

case = json.load(open("case.json"))
order = case["files"]["orders/HZ-260511-03.txt"]
policy = case["files"]["docs/aftercare-policy.md"]

# the order must hit the trade-in exception, otherwise the case is broken
assert re.search(r"以旧换新", order), "order is not a trade-in purchase"
assert re.search(r"整机", order), "order does not cover a whole unit"
assert re.search(r"保修\s*24\s*个月", policy), "standard clause absent"

m = re.search(r"以旧换新活动购入的整机产品[：:]\s*整机保修\s*(\d+)\s*个月", policy)
assert m, "trade-in exception clause absent"
print(json.dumps({"expected_number": int(m.group(1))}))
