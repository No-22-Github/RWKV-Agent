# WORKBANK-CANARY-c5813e6a : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

serve = next(e for e in case["web_fixture"] if "docs.quillmark.dev" in e.get("url", ""))
row = re.search(r"\|\s*--port\s*\|\s*(\d+)\s*\|", serve["content"])
assert row, "--port row not found in fixture content"
print(json.dumps({"expected": row.group(1)}))
