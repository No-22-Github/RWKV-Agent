# WORKBANK-CANARY-c4d05e88 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))

# A tracked marker is a comment line given over to the tag on a line of its
# own (leading indentation is fine); tags inside strings, format templates or
# trailing remarks do not count.
tracked = re.compile(r"^\s*#\s*TODO\b")
total = 0
for path in sorted(case["files"]):
    if not path.endswith(".py"):
        continue
    for line in case["files"][path].split("\n"):
        if tracked.match(line):
            total += 1

print(json.dumps({"expected_number": total}))
