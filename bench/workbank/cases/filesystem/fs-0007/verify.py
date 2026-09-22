# WORKBANK-CANARY-2ad58e40 : bank artifact, excluded from training corpora
"""Expected answer for fs-0007: the biggest file in the live title's folder.

The scope is the production folder of the title in production, which README.md
names; the retired title's mirrored folder is not part of it. Sizes are the
byte lengths of the stored file contents.
"""
import json

LIVE = "titles/nettlewick/"

case = json.load(open("case.json"))
files = case["files"]

scope = {path: content for path, content in files.items() if path.startswith(LIVE)}
if not scope:
    raise SystemExit("no files under %s" % LIVE)

sizes = {path: len(content.encode("utf-8")) for path, content in scope.items()}
biggest = max(sizes, key=lambda path: sizes[path])
ties = sorted(path for path, size in sizes.items() if size == sizes[biggest])
if len(ties) != 1:
    raise SystemExit("no single biggest file under %s: %s" % (LIVE, ties))
print(json.dumps({"expected": biggest}))
