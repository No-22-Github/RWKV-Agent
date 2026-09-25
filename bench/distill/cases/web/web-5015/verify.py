# DISTILL-CANARY-1e7d3c05 : distillation case
"""Recompute the QR-8802 row ceiling from the Quarryside error page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
match = re.search(r"carries more than (\d+) rows", page)
if match is None:
    raise SystemExit("the error page does not state the row ceiling")
ceiling = int(match.group(1))
assert "QR-8802" in page, "the ceiling must belong to the too-large import error"
print(json.dumps({"expected_number": ceiling}))
