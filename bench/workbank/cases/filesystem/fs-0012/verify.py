# WORKBANK-CANARY-c93f6d18 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]
# Group every file by its exact stored bytes; the release holds one artifact
# as two byte-identical files under release/manifest/.
by_content = {}
for path, content in files.items():
    by_content.setdefault(content, []).append(path)
groups = [sorted(paths) for paths in by_content.values() if len(paths) > 1]
answer = groups[0][0] if len(groups) == 1 else "UNKNOWN"
print(json.dumps({"expected": answer}))
