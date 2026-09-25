# DISTILL-CANARY-04e31b1c : distillation case
import json

MARKER = "CURE-WAIT"
PACKAGE = "curing/"
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


count = 0
for path, text in case["files"].items():
    if not path.startswith(PACKAGE):
        continue
    for line in text.splitlines():
        if MARKER in comment_part(line):
            count += 1
print(json.dumps({"expected_number": count}))
