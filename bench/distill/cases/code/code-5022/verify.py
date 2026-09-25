# DISTILL-CANARY-07d3b96e : distillation case
import json

MARKER = "SPINDLE-HOLD"
PACKAGE = "spinning/"
case = json.load(open("case.json"))


def comment_part(line):
    quote = None
    index = 0
    while index < len(line):
        char = line[index]
        if quote is not None:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if char == "#":
            return line[index:]
        index += 1
    return ""


files = 0
for path, text in case["files"].items():
    if not path.startswith(PACKAGE):
        continue
    for line in text.splitlines():
        if MARKER in comment_part(line):
            files += 1
            break
print(json.dumps({"expected_number": files}))
