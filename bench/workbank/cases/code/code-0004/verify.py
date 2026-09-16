import json
import re

case = json.load(open("case.json"))
py_tag = re.compile(r"^#\s*(TODO|FIXME)\b")
plain_tag = re.compile(r"^(TODO|FIXME)\b")
total = 0
for path in sorted(case["files"]):
    for line in case["files"][path].split("\n"):
        stripped = line.lstrip()
        if path.endswith(".py"):
            if py_tag.match(stripped):
                total += 1
        elif plain_tag.match(stripped):
            total += 1
print(json.dumps({"expected_number": total}))
