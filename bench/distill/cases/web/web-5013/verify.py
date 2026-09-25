# DISTILL-CANARY-4c1a7e93 : distillation case
"""Recompute the idle_expiry_days default from the Fernwharf reference page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
match = re.search(r"idle_expiry_days \| (\d+) \|", page)
if match is None:
    raise SystemExit("the reference page carries no idle_expiry_days row")
expiry = int(match.group(1))
letters = int(re.search(r"dead_letter_expiry_days \| (\d+) \|", page).group(1))
assert expiry != letters, "the answer must differ from the dead letter expiry"
print(json.dumps({"expected_number": expiry}))
