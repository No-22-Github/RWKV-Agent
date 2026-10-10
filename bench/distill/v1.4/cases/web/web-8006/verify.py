# DISTILL-CANARY-17b89596 : distillation case
import json
import re

case = json.load(open("case.json"))
dep = [w for w in case["web_fixture"] if w["url"] == "https://docs.ostrander.com/deprecations"][0]["content"]
assert re.search(r"\| /v1/batch \| deprecated.*\| 2026-12-01", dep)
print(json.dumps({"expected_contains_any": ["2026-12-01", "December 1, 2026", "1 December 2026", "Dec 1, 2026"]}))
