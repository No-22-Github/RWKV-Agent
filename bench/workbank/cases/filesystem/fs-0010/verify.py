# WORKBANK-CANARY-a1d6f0c3 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]
# Group every file by its exact stored bytes; a duplication audit needs a
# group with more than one member.
by_content = {}
for path, content in files.items():
    by_content.setdefault(content, []).append(path)
groups = [sorted(paths) for paths in by_content.values() if len(paths) > 1]
answer = groups[0][0] if len(groups) == 1 else "UNKNOWN"
print(json.dumps({"expected": answer}))
