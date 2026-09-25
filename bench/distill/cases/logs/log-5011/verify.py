# DISTILL-CANARY-16cc7427 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/feed-loader.log"].splitlines() if line.strip()]
closing = re.fullmatch(
    r"\S+ INFO +run finished date=(\d{4}-\d{2}-\d{2}) accepted=(\d+) rejected=(\d+)", lines[-1])
assert closing is not None, "run summary line missing"
assert closing.group(1) == "2026-09-04", "unexpected run date"
rejected = [line for line in lines[:-1] if " rejected reason=" in line]
assert len(rejected) == int(closing.group(3)), "the journal does not list every rejected SKU"
no_currency = [line for line in rejected if line.endswith("reason=missing_currency")]
print(json.dumps({"expected_number": len(no_currency)}))
