# DISTILL-CANARY-a97b24f1 : distillation case
"""Recompute the notice window from the Tarnwell deprecation notice."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
match = re.search(r"accepting requests for (\d+)\s+days", page)
if match is None:
    raise SystemExit("the notice does not state the window")
days = int(match.group(1))
assert re.search(r"answered\s+410", page), "the notice must say what happens after the window"
print(json.dumps({"expected_number": days}))
