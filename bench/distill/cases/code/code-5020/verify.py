# DISTILL-CANARY-5b7f2d48 : distillation case
import json
import re

NAME = "tally_draw"
TARGET = "melt/store.py"
case = json.load(open("case.json"))

call = re.compile(r"(?<![\w.])" + NAME + r"\s*\(")

count = 0
for path, text in case["files"].items():
    if not path.startswith("crews/"):
        continue
    local = None
    for line in text.splitlines():
        match = re.match(r"from\s+([\w.]+)\s+import\s+([\w, ]+)$", line)
        if not match:
            continue
        module = match.group(1).replace(".", "/") + ".py"
        names = [piece.strip() for piece in match.group(2).split(",")]
        if NAME in names:
            local = module
    if local != TARGET:
        continue
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        count += len(call.findall(line))
print(json.dumps({"expected_number": count}))
