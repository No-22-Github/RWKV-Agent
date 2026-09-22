# WORKBANK-CANARY-b62d8e04 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

ref = next(e for e in case["web_fixture"]
           if "docs.copperlane.io/reference/errors" in e.get("url", ""))
rows = re.findall(r"\|\s*CL-5812\s*\|\s*([a-z]+)\s*\|", ref["content"])
assert len(rows) == 1, "expected exactly one CL-5812 row, found %r" % rows
print(json.dumps({"expected_condition": rows[0]}))
