# DISTILL-CANARY-5ba7c148 : distillation case
"""Recompute the PD-2004 backoff from the Peldreth channel reference."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
channel = int(re.search(r"PD-2004 \| channel output buffer overflowed \| back off for (\d+) seconds",
                        pages["https://docs.peldreth.example/channels/error-codes"]).group(1))
relay = int(re.search(r"PR-3117 \| relay handshake reset by the peer \| back off for (\d+) seconds",
                      pages["https://docs.peldreth.example/relay/error-codes"]).group(1))
assert channel != relay, "the relay page must not repeat the channel backoff"
print(json.dumps({"expected_number": channel}))
