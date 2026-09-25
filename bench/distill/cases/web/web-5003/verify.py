# DISTILL-CANARY-b58e0f31 : distillation case
"""Recompute the TB-4021 retry wait from the Thistlebay troubleshooting page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
wait = int(re.search(r"TB-4021 \| upstream handshake timeout \| wait (\d+) seconds", page).group(1))
pool = int(re.search(r"TB-5030 \| upstream connection pool exhausted \| wait (\d+) seconds", page).group(1))
assert wait != pool, "the answer must differ from the neighbouring TB-5030 wait"
print(json.dumps({"expected_number": wait}))
