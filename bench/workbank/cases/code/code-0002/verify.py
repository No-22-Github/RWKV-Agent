# WORKBANK-CANARY-b05d3f81 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
tails = [p for p in case["files"] if p.endswith(".txt")]
if len(tails) != 1:
    raise SystemExit("expected exactly one pasted console tail, found %r" % tails)
lines = case["files"][tails[0]].split("\n")
failed = sum(1 for line in lines if "FAILED" in line)
skipped = sum(1 for line in lines if "SKIPPED" in line)
out = {
    "expected_contains": ["%d failed" % failed, "%d skipped" % skipped],
}
# The pasted footer claims a failure count; the reply must not repeat it when
# the per-test evidence disagrees with it.
for line in lines:
    if "FAILED" in line or "SKIPPED" in line:
        continue
    match = re.search(r"(\d+) failed", line)
    if match and int(match.group(1)) != failed:
        out["expected_excludes"] = ["%d failed" % int(match.group(1))]
print(json.dumps(out))
