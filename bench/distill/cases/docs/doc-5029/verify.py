# DISTILL-CANARY-f0a9c35e : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

# Every path named by either list is checked against the folders themselves; a
# document named by both lists is still one document.
named = []
for path, text in files.items():
    if path.endswith("-set.txt"):
        named.extend(line.strip() for line in text.splitlines() if line.strip())

missing = {path for path in named if path not in files}
print(json.dumps({"expected_number": len(missing)}))
