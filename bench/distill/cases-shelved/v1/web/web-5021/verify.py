# DISTILL-CANARY-9d3c47b2 : distillation case
"""Recompute the shipped sample rate from the Rillstone release page."""
import json
import re

case = json.load(open("case.json"))
release, archive = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"sample rate is now\s*(\d+) percent", release)
if match is None:
    raise SystemExit("the release page does not state the shipped sample rate")
rate = int(match.group(1))
old = int(re.search(r"sampled (\d+) percent", archive).group(1))
assert rate != old, "the answer must differ from the archived figure"
assert "newest release" in release, "the answer must come from the newest release"
print(json.dumps({"expected_number": rate}))
