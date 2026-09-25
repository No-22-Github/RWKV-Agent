# DISTILL-CANARY-e3a95c7f : distillation case
import json
import re

NAME = "post_reading"
case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import [\w, ]*\b" + NAME + r"\b")
call = re.compile(r"(?<![\w.])" + NAME + r"\s*\(")

count = 0
for text in case["files"].values():
    lines = text.splitlines()
    if any(re.match(r"^def " + NAME + r"\(", line) for line in lines):
        continue
    if not any(binding.match(line) for line in lines):
        continue
    for line in lines:
        if line.strip().startswith("#"):
            continue
        count += len(call.findall(line))
print(json.dumps({"expected_number": count}))
