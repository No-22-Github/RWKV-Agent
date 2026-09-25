# DISTILL-CANARY-9f32d5ca : distillation case
"""Recompute the standard-queue visibility default from the Saltmarsh reference."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
standard = int(re.search(r"defaults to (\d+) seconds for standard queues",
                         pages["https://docs.saltmarsh.example/reference/queues"]).group(1))
batch = int(re.search(r"for batch queues\s+defaults to (\d+) seconds",
                      pages["https://docs.saltmarsh.example/reference/batch-queues"]).group(1))
assert standard != batch, "the competing page must not repeat the answer"
print(json.dumps({"expected_number": standard}))
