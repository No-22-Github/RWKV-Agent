# DISTILL-CANARY-bd72e0a4 : distillation case
import json
import re

case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import [\w, ]*\bSink\b")
call = re.compile(r"\bsink\.emit\s*\(")

count = 0
for path, text in case["files"].items():
    lines = text.splitlines()
    if not any(binding.match(line) for line in lines):
        continue
    for line in lines:
        if line.strip().startswith("#"):
            continue
        count += len(call.findall(line))
print(json.dumps({"expected_number": count}))
