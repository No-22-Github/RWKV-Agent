# DISTILL-CANARY-5f4e21d7 : distillation case
"""Recompute the shipped worker count from the Skerriford release page."""
import json
import re

case = json.load(open("case.json"))
release, guide = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"worker count is now (\d+)", release)
if match is None:
    raise SystemExit("the release page does not state the shipped worker count")
workers = int(match.group(1))
guide_workers = int(re.search(r"worker count to (\d+)", guide).group(1))
assert workers != guide_workers, "the answer must differ from the install guide figure"
assert "newest release" in release, "the answer must come from the newest release"
print(json.dumps({"expected_number": workers}))
