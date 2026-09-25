# DISTILL-CANARY-08f3cc59 : distillation case
import json
import re

NAME = "check_trim"
SCOPES = ("decks/", "hulls/")
case = json.load(open("case.json"))

binding = re.compile(r"^from [\w.]+ import\s+([\w, ]+)\s*$")

count = 0
for path, text in case["files"].items():
    if not path.startswith(SCOPES):
        continue
    local = ""
    for line in text.splitlines():
        match = binding.match(line)
        if not match:
            continue
        for part in match.group(1).split(","):
            piece = part.strip().split(" as ")
            if piece[0] == NAME:
                local = piece[1] if len(piece) > 1 else NAME
    if not local:
        continue
    call = re.compile(r"(?<![\w.])" + re.escape(local) + r"\s*\(")
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        count += len(call.findall(line))
print(json.dumps({"expected_number": count}))
