# WORKBANK-CANARY-3a7f1c9e : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

ref = next(e for e in case["web_fixture"]
           if "docs.kelpgate.dev/reference/error-codes" in e.get("url", ""))
rows = re.findall(r"\|\s*KG-4021\s*\|\s*([a-z]+)\s*\|", ref["content"])
assert len(rows) == 1, "expected exactly one KG-4021 row, found %r" % rows
print(json.dumps({"expected_condition": rows[0]}))
