# DISTILL-CANARY-7c1d4a92 : distillation case
"""Recompute the flush_interval_ms default from the Kelpforge reference page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
interval = int(re.search(r"flush_interval_ms \| (\d+) \|", page).group(1))
batch = int(re.search(r"flush_batch_size \| (\d+) \|", page).group(1))
assert interval != batch, "the answer must differ from the batch size default"
print(json.dumps({"expected_number": interval}))
