# DISTILL-CANARY-83e1d60c : distillation case
import json
import re

NAME = "record_weighing"
case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import [\w, ]*\b" + NAME + r"\b")
call = re.compile(r"(?<![\w.])" + NAME + r"\s*\(")

count = 0
for path, text in case["files"].items():
    if not (path.startswith("intake/") or path.startswith("pond/")):
        continue
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
