# WORKBANK-CANARY-e63b91c7 : bank artifact, excluded from training corpora
"""Expected answer for fs-0008: the byte size of the biggest file in the archive.

The archive is surveys/, which README.md defines; transfers/ holds outbound
staging copies of the same series and is not part of it. Sizes are the byte
lengths of the stored file contents, and the biggest one is unique.
"""
import json

ARCHIVE = "surveys/"

case = json.load(open("case.json"))
files = case["files"]

scope = {path: content for path, content in files.items() if path.startswith(ARCHIVE)}
if not scope:
    raise SystemExit("no files under %s" % ARCHIVE)

sizes = {path: len(content.encode("utf-8")) for path, content in scope.items()}
biggest = max(sizes.values())
winners = sorted(path for path, size in sizes.items() if size == biggest)
if len(winners) != 1:
    raise SystemExit("no single biggest file under %s: %s" % (ARCHIVE, winners))
print(json.dumps({"expected_number": biggest}))
