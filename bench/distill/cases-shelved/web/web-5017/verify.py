# DISTILL-CANARY-36d0c8be : distillation case
"""Recompute the live SH-4410 wait from the Sheldwich error pages."""
import json
import re

case = json.load(open("case.json"))
live, trial = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"SH-4410 \| duplicate settlement request \| retry the same request after (\d+) seconds", live)
if match is None:
    raise SystemExit("the live reference carries no SH-4410 row")
wait = int(match.group(1))
trial_wait = int(re.search(r"SH-4410 \| retry after (\d+) seconds", trial).group(1))
assert wait != trial_wait, "the answer must differ from the trial timer"
assert "live" in live, "the answer must come from the page for the live platform"
print(json.dumps({"expected_number": wait}))
