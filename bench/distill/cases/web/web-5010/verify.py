# DISTILL-CANARY-d9032f6a : distillation case
"""Recompute the standard-plan send rate from the Windrow reference."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
standard = int(re.search(r"standard plan may send (\d+) messages per second",
                         pages["https://docs.windrow.example/reference/limits"]).group(1))
trial = int(re.search(r"trial workspace may send (\d+) messages per second",
                      pages["https://docs.windrow.example/reference/trial-limits"]).group(1))
assert standard != trial, "the trial page must not repeat the standard rate"
print(json.dumps({"expected_number": standard}))
