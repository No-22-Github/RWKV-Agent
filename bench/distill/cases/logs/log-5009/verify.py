# DISTILL-CANARY-bf14ca4b : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/feed-loader.log"].splitlines() if line.strip()]
closing = re.fullmatch(
    r"\S+ INFO +run finished date=\d{4}-\d{2}-\d{2} accepted=(\d+) rejected=(\d+)", lines[-1])
assert closing is not None, "run summary line missing"
rejected = [line for line in lines[:-1] if " rejected reason=" in line]
assert len(rejected) == int(closing.group(2)), "the journal does not list every rejected SKU"

# The journal records only the SKUs that were turned away, with a reason code and
# no price at all, so nothing in the workspace says how the accepted SKUs' prices
# compare with the previous list.
print(json.dumps({"expected_string": "UNKNOWN"}))
