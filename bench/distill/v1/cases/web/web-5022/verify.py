# DISTILL-CANARY-e6a1508c : distillation case
"""Recompute the AC-4210 hop ceiling from the Ashcott error page."""
import json
import re

case = json.load(open("case.json"))
errors, limits = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"follows more than (\d+) redirect hops", errors)
if match is None:
    raise SystemExit("the error page does not state the hop ceiling")
ceiling = int(match.group(1))
rule_hops = int(re.search(r"through (\d+) internal hops", limits).group(1))
assert ceiling != rule_hops, "the answer must differ from the edge rule figure"
assert "seventeenth" in errors, "the ceiling must be the one the error is raised at"
print(json.dumps({"expected_number": ceiling}))
