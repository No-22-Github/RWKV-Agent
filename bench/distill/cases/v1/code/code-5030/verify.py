# DISTILL-CANARY-ad913d6e : distillation case
import json
import re

NAME = "grade_oyster"
SCOPES = ("beds/", "trays/")
case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import [\w, ]*\b" + NAME + r"\b")
call = re.compile(r"(?<![\w.])" + NAME + r"\s*\(")

count = 0
for path, text in case["files"].items():
    if not path.startswith(SCOPES):
        continue
    lines = text.splitlines()
    if not any(binding.match(line) for line in lines):
        continue
    for line in lines:
        if line.strip().startswith("#"):
            continue
        count += len(call.findall(line))
print(json.dumps({"expected_number": count}))
