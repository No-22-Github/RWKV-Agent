# DISTILL-CANARY-2b9f7de4 : distillation case
"""Recompute the drain batch size from the Cobbleyard reference page."""
import json
import re

case = json.load(open("case.json"))
reference, plan = (entry["content"] for entry in case["web_fixture"])
match = re.search(r"batch_messages \| (\d+) \|", reference)
if match is None:
    raise SystemExit("the reference page carries no batch_messages row")
size = int(match.group(1))
plan_size = int(re.search(r"batches of\s+(\d+) messages", plan).group(1))
assert size != plan_size, "the answer must differ from the entry plan figure"
assert "full relay" in reference, "the answer must be the full relay default"
print(json.dumps({"expected_number": size}))
