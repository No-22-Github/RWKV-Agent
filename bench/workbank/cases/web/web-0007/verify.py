# WORKBANK-CANARY-a37d5e02 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

page = next(e for e in case["web_fixture"]
            if "docs.tidalforge.dev/reference/deprecations" in e.get("url", ""))
row = re.search(r"\|\s*media_priority\s*\|\s*([0-9][0-9.]*)\s*\|", page["content"])
assert row, "media_priority row not found in the deprecations table"
print(json.dumps({"expected": row.group(1)}))
