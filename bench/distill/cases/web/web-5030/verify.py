# DISTILL-CANARY-5c93b1e8 : distillation case
"""Recompute the Hallowbrook body ceiling from the ingest error page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
ceiling = int(re.search(r"a single request body goes past (\d+) kilobytes", pages).group(1))
buffer_kib = int(re.search(r"buffers (\d+) kilobytes of an incoming body", pages).group(1))
if ceiling == buffer_kib:
    raise SystemExit("the body ceiling and the buffer size must differ")
print(json.dumps({"expected_number": ceiling}))
