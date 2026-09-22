# WORKBANK-CANARY-2e8b41c9 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

page = next(e for e in case["web_fixture"]
            if "glasswren.dev/release-notes" in e.get("url", ""))
blocks = [b for b in re.split(r"\n## ", page["content"])
          if "analyzer_chain" in b and "Deprecated:" in b]
assert len(blocks) == 1, "expected exactly one release note block deprecating analyzer_chain"
version = blocks[0].split(None, 1)[0]
assert re.fullmatch(r"[0-9][0-9.]*", version), version
print(json.dumps({"expected": version}))
