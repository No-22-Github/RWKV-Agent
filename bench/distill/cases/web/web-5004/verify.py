# DISTILL-CANARY-2ad96c47 : distillation case
"""Recompute the newest release's pool default from the Bramblewick release page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
sizes = re.findall(r"default connection pool size (?:raised from \d+ to|stays at) (\d+)", page)
assert len(sizes) >= 2, "the page must list more than one release"
assert sizes[0] != sizes[-1], "the newest release must differ from the older ones"
print(json.dumps({"expected_number": int(sizes[0])}))
