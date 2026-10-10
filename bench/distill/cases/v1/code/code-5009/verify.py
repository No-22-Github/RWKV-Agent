# DISTILL-CANARY-38c5f1ae : distillation case
import json
import re

NAME = "seal_lot"
case = json.load(open("case.json"))

caller = ""
for path, text in sorted(case["files"].items()):
    lines = text.splitlines()
    if any(re.match(r"^def " + NAME + r"\(", line) for line in lines):
        continue
    bound = any(re.match(r"^from [\w.]+ import [\w, ]*\b" + NAME + r"\b", line) for line in lines)
    called = any(
        not line.strip().startswith("#") and re.search(r"(?<![\w.])" + NAME + r"\s*\(", line)
        for line in lines
    )
    if bound and called:
        caller = path
print(json.dumps({"expected_string": caller}))
