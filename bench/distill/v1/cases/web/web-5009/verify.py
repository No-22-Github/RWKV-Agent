# DISTILL-CANARY-18e5a3b9 : distillation case
"""Recompute the v1 orders retirement window from the Quillstone notices."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
orders = int(re.search(r"opens a (\d+)-day window",
                       pages["https://quillstone.example/migrations/v1-orders"]).group(1))
shipments = int(re.search(r"opens a (\d+)-day window",
                          pages["https://quillstone.example/migrations/v1-shipments"]).group(1))
assert orders != shipments, "the shipments notice must not repeat the orders window"
print(json.dumps({"expected_number": orders}))
