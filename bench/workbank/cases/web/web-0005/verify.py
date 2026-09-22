# WORKBANK-CANARY-6c1f0a7d : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

page = next(e for e in case["web_fixture"]
            if "docs.cindermill.io/reference/deprecations" in e.get("url", ""))
row = re.search(r"\|\s*remote_verify\s*\|\s*([0-9][0-9.]*)\s*\|", page["content"])
assert row, "remote_verify row not found in the deprecations table"
print(json.dumps({"expected": row.group(1)}))
