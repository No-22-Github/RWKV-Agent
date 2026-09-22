# WORKBANK-CANARY-cc41b7f2 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

ref = next(e for e in case["web_fixture"]
           if "docs.harborlight.io/reference/errors" in e.get("url", ""))
rows = re.findall(r"\|\s*HL-3312\s*\|\s*([a-z]+)\s*\|", ref["content"])
assert len(rows) == 1, "expected exactly one HL-3312 row, found %r" % rows
# The decoy code must resolve to a different condition name on the same page.
decoy = re.findall(r"\|\s*HL-3132\s*\|\s*([a-z]+)\s*\|", ref["content"])
assert decoy == ["tidebreak"], "decoy row changed: %r" % decoy
assert decoy[0] != rows[0], "decoy condition equals the answer"
print(json.dumps({"expected_condition": rows[0]}))
