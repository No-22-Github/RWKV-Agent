# DISTILL-CANARY-c41b8f07 : distillation case
"""Recompute the attempt ceiling behind CB-1077 from the Coldbridge page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
ceiling = int(re.search(r"more than (\d+) attempts in a rolling hour", page).group(1))
pause = int(re.search(r"leave the card for (\d+) seconds", page).group(1))
if ceiling == pause:
    raise SystemExit("the attempt ceiling and the retry pause must differ")
print(json.dumps({"expected_number": ceiling}))
