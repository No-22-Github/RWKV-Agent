# DISTILL-CANARY-8b2f60ad : distillation case
"""Recompute the shipped shard count from the Harrowden release notes."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
match = re.search(r"spreads over (\d+) shards", page)
if match is None:
    raise SystemExit("the release notes do not state the shipped shard count")
shards = int(match.group(1))
previous = int(re.search(r"instead of (\d+)", page).group(1))
assert shards != previous, "the answer must differ from the superseded figure"
print(json.dumps({"expected_number": shards}))
