# DISTILL-CANARY-c7f10d5e : distillation case
"""Recompute the newest Python SDK retry default from the Marshlight releases."""
import json
import re

case = json.load(open("case.json"))
pages = {page["url"]: page["content"] for page in case["web_fixture"]}
python = re.findall(r"default retry attempts raised from \d+ to (\d+)",
                    pages["https://marshlight.example/python-sdk/releases"])
node = re.findall(r"default retry attempts raised from \d+ to (\d+)",
                  pages["https://marshlight.example/node-sdk/releases"])
assert len(python) == 1 and len(node) == 1, "each release page states one new default"
assert python[0] != node[0], "the Node SDK page must not repeat the answer"
print(json.dumps({"expected_number": int(python[0])}))
