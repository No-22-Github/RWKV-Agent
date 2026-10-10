# DISTILL-CANARY-2c95a7f3 : distillation case
import json
import re

NAME = "freeze_run"
DEFINER = "store/chill.py"
case = json.load(open("case.json"))

callers = []
for path, text in case["files"].items():
    local = None
    for line in text.splitlines():
        match = re.match(r"from\s+([\w.]+)\s+import\s+([\w, ]+)$", line)
        if not match:
            continue
        module = match.group(1).replace(".", "/") + ".py"
        for part in match.group(2).split(","):
            names = [piece.strip() for piece in part.strip().split(" as ")]
            if names and names[0] == NAME and module == DEFINER:
                local = names[1] if len(names) > 1 else NAME
    if local is None:
        continue
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        if re.search(r"(?<![\w.])" + re.escape(local) + r"\s*\(", line):
            callers.append(path)
            break
print(json.dumps({"expected_string": callers[0] if len(callers) == 1 else ""}))
