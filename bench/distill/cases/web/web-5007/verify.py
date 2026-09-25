# DISTILL-CANARY-46b8e207 : distillation case
"""Recompute the live OB-1130 retry wait from the Otterbourne reference."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
live = int(re.search(r"OB-1130 \| settlement window closed for today \| retry the same request after (\d+) seconds",
                     pages["https://docs.otterbourne.example/errors/live"]).group(1))
sandbox = int(re.search(r"OB-1130 \| retry after (\d+) seconds",
                        pages["https://docs.otterbourne.example/errors/sandbox"]).group(1))
assert live != sandbox, "the sandbox page must not repeat the live wait"
print(json.dumps({"expected_number": live}))
