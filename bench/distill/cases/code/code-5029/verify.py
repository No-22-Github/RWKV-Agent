# DISTILL-CANARY-534001ad : distillation case
import json
import re

NAME = "bend_sail"
case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import [\w, ]*\b" + NAME + r"\b")
call = re.compile(r"(?<![\w.])" + NAME + r"\s*\(")

caller = ""
for path in sorted(case["files"]):
    lines = case["files"][path].splitlines()
    if any(re.match(r"^def " + NAME + r"\(", line) for line in lines):
        continue
    if not any(binding.match(line) for line in lines):
        continue
    if any(not line.strip().startswith("#") and call.search(line) for line in lines):
        caller = path
print(json.dumps({"expected_string": caller}))
