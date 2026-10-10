# DISTILL-CANARY-e4017b83 : distillation case
"""Recompute the v1 invoice retirement window from the Cinderpath notice."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
window = int(re.search(r"opens a (\d+)-day window", page).group(1))
kept = int(re.search(r"for (\d+) days after the notice the", page).group(1))
assert window == kept, "the notice must state one window length"
print(json.dumps({"expected_number": window}))
