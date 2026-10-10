# DISTILL-CANARY-6e2a97c5 : distillation case
"""Recompute the Silverdale v2 notice period ceiling from the notice page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
notice = int(re.search(r"it is held to (\d+) calls per minute", pages).group(1))
v3 = int(re.search(r"v3 tracking feed accepts (\d+) calls per minute", pages).group(1))
if notice == v3:
    raise SystemExit("the v2 notice ceiling and the v3 ceiling must differ")
print(json.dumps({"expected_number": notice}))
