# DISTILL-CANARY-48c3f9a1 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]

target = ""
for line in files["nightly.py"].splitlines():
    match = re.match(r"from\s+([A-Za-z_][\w.]*)\s+import\s+TIDE_MARGIN_MINUTES\s*$", line)
    if match:
        path = match.group(1).replace(".", "/") + ".py"
        if re.search(r"(?m)^TIDE_MARGIN_MINUTES\s*=", files.get(path, "")):
            target = path
print(json.dumps({"expected_string": target}))
