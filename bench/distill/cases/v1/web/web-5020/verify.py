# DISTILL-CANARY-70e5d1fa : distillation case
"""Recompute the production overlap from the Steepholm sunset notices."""
import json
import re

case = json.load(open("case.json"))
production, sandbox = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"production keys (\d+) days", production)
if match is None:
    raise SystemExit("the sunset notice does not state the production overlap")
days = int(match.group(1))
sandbox_days = int(re.search(r"switched off (\d+) days", sandbox).group(1))
assert days != sandbox_days, "the answer must differ from the sandbox figure"
assert "does not cover sandbox keys" in production, "the production notice must exclude sandbox keys"
print(json.dumps({"expected_number": days}))
