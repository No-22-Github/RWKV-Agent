# WORKBANK-CANARY-5f0a93d1 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

index = next(e for e in case["web_fixture"]
             if "docs.tiderail.dev/errors/trd-1094" in e.get("url", ""))
# The condition name is stated in the result snippet and in the index table.
in_snippet = re.search(r"TRD-1094 reports a ([a-z]+)", index["snippet"])
rows = re.findall(r"\|\s*TRD-1094\s*\|\s*([a-z]+)\s*\|", index["content"])
assert len(rows) == 1, "expected exactly one TRD-1094 row, found %r" % rows
assert in_snippet and in_snippet.group(1) == rows[0], "snippet and table disagree: %r vs %r" % (
    in_snippet and in_snippet.group(1), rows)
print(json.dumps({"expected_condition": rows[0]}))
