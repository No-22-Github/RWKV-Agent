# DISTILL-CANARY-9e4a07d3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]

target = ""
for line in files["jobs/rotation.py"].splitlines():
    match = re.match(r"from\s+([A-Za-z_][\w.]*)\s+import\s+rotate_shards\s*$", line)
    if match:
        module = match.group(1).replace(".", "/") + ".py"
        if re.search(r"(?m)^def rotate_shards\(", files.get(module, "")):
            target = module
print(json.dumps({"expected_string": target}))
