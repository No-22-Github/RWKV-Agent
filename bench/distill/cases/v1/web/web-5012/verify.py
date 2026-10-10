# DISTILL-CANARY-a2f60e74 : distillation case
"""Recompute the newest Python client batch size from the Rookhaven releases."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
python = [int(v) for v in re.findall(r"default batch size (?:raised to|stays at) (\d+) rows",
                                     pages["https://rookhaven.example/clients/python/releases"])]
go = [int(v) for v in re.findall(r"default batch size (?:raised to|stays at) (\d+) rows",
                                 pages["https://rookhaven.example/clients/go/releases"])]
assert len(python) >= 2 and len(go) >= 1, "both release pages must list defaults"
assert python[0] != go[0], "the Go client page must not repeat the answer"
print(json.dumps({"expected_number": python[0]}))
