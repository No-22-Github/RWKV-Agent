# DISTILL-CANARY-2d58c0fe : distillation case
"""Recompute the Yarnbrook read timeout from the collector defaults page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
timeout = int(re.search(r"read_timeout_seconds \| (\d+) \|", pages).group(1))
flush = int(re.search(r"flush_interval_seconds \| (\d+) \|", pages).group(1))
field_kit = int(re.search(r"gives up after (\d+) seconds", pages).group(1))
if len({timeout, flush, field_kit}) != 3:
    raise SystemExit("the timeout, the flush interval and the field kit timing must differ")
print(json.dumps({"expected_number": timeout}))
