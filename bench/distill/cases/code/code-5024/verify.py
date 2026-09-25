# DISTILL-CANARY-e2181ab3 : distillation case
import json
import re

NAME = "weigh_bundle"
case = json.load(open("case.json"))
files = case["files"]

target = ""
for path in sorted(files):
    for line in files[path].splitlines():
        match = re.match(r"^from\s+([A-Za-z_][\w.]*)\s+import\s+" + NAME + r"\s*$", line)
        if not match:
            continue
        module = match.group(1).replace(".", "/") + ".py"
        if re.search(r"(?m)^def " + NAME + r"\(", files.get(module, "")):
            target = module
print(json.dumps({"expected_string": target}))
