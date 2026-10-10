# DISTILL-CANARY-bf14ca4b : distillation case
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"]
log = case["files"]["logs/feed-loader.log"]
assert readme.startswith("# price-feed loader\n"), "README.md does not document the journal"
lines = [line for line in log.splitlines() if line.strip()]
closing = re.fullmatch(
    r"\S+ INFO +run finished date=\d{4}-\d{2}-\d{2} accepted=(\d+) rejected=(\d+)", lines[-1])
assert closing is not None, "run summary line missing"
rejected = [line for line in lines[:-1] if " rejected reason=" in line]
assert len(rejected) == int(closing.group(2)), "the journal does not list every rejected SKU"

# The journal records only the SKUs that were turned away, each with a reason
# code and no price at all, and the closing line carries counts alone, so the
# workspace holds zero records of the accepted SKUs' prices.
warn_re = re.compile(
    r"\S+ WARN +sku=\S+ rejected reason=(missing_currency|pack_size_missing|price_out_of_range)")
for line in lines[:-1]:
    assert warn_re.fullmatch(line), "unexpected journal line: " + line
assert "price=" not in readme + log, "a price record appeared in the workspace"
print(json.dumps({"expected_contains_any": ["price comparison", "prices", "compare", "previous list"]}))
