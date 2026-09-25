# DISTILL-CANARY-c2b8a930 : distillation case
"""Recompute the standard lease from the Landwick reference page."""
import json
import re

case = json.load(open("case.json"))
reference, walkthrough = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"lease_seconds \| (\d+) \|", reference)
if match is None:
    raise SystemExit("the reference page carries no lease_seconds row")
lease = int(match.group(1))
demo = int(re.search(r"lease to (\d+) seconds", walkthrough).group(1))
assert lease != demo, "the answer must differ from the walkthrough lease"
assert "| setting | default |" in reference, "the answer must come from the defaults table"
print(json.dumps({"expected_number": lease}))
