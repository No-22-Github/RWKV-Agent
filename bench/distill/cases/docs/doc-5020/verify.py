# DISTILL-CANARY-c25a91f8 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

# Every path named by either register is checked against the folders, and the
# registers between them name the documents the centre works from.
named = []
for path, text in files.items():
    if path.endswith("-register.txt"):
        named.extend(line.strip() for line in text.splitlines() if line.strip())

missing = {path for path in named if path not in files}
print(json.dumps({"expected_number": len(missing)}))
