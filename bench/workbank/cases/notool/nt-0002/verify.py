# WORKBANK-CANARY-b58c20f7 : bank artifact, excluded from training corpora
import json
import re

# Default ports are stable IANA assignments, so the expectation comes from a
# fixed knowledge table plus the protocol actually named in the prompt — never
# copied from the expect block.
DEFAULT_PORTS = {"https": "443", "http": "80", "ssh": "22", "smtp": "25"}

case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"].lower()
named = [p for p in DEFAULT_PORTS if re.search(r"\b%s\b" % p, prompt)]
if len(named) != 1:
    raise SystemExit("expected exactly one protocol in prompt, found %r" % (named,))
print(json.dumps({"expected": DEFAULT_PORTS[named[0]]}))
