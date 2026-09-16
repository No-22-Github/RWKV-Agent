# WORKBANK-CANARY-7c41a9e2 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
target = "acquire_session_lock"
pattern = re.compile(r"^\s*def\s+" + re.escape(target) + r"\s*\(")
hits = []
for path in sorted(case["files"]):
    for lineno, line in enumerate(case["files"][path].split("\n"), 1):
        if pattern.match(line):
            hits.append("%s:%d" % (path, lineno))
if len(hits) != 1:
    raise SystemExit("expected exactly one definition of %s, found %r" % (target, hits))
print(json.dumps({"expected": hits[0]}))
